"""Owner-scoped phone accounts with encrypted, durable provider credentials."""
from __future__ import annotations

import base64
import json
import os
import re
import threading
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta

from Crypto.Cipher import AES
from sqlalchemy.exc import IntegrityError

from app.util import ensure_api_key
from webapp.db import AppUser, ProviderAccount, SessionLocal, init_db

_SQLITE_ACCOUNT_LOCK = threading.RLock()


@contextmanager
def _account_session():
    """Serialize local SQLite operations; PostgreSQL uses owner/row locks.

    The SQLite lock is process-local. Use one development server process with
    SQLite; shared deployments and multiple workers require PostgreSQL.
    """
    with ExitStack() as stack:
        db = SessionLocal()
        if db.get_bind().dialect.name == "sqlite":
            stack.enter_context(_SQLITE_ACCOUNT_LOCK)
        # Close the session before releasing the SQLite lock.
        stack.enter_context(db)
        yield db


@dataclass
class ActiveUser:
    number: int
    subscriber_id: str
    subscription_type: str
    tokens: dict


class ProviderAccountError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _encryption_key() -> bytes:
    configured = os.environ.get("TOKEN_ENCRYPTION_KEY", "").strip()
    if not configured:
        raise ProviderAccountError("TOKEN_ENCRYPTION_KEY belum diatur. Hubungi pengelola aplikasi.", 503)
    try:
        if not re.fullmatch(r"[A-Za-z0-9_-]+={0,2}", configured):
            raise ValueError("Invalid base64")
        key = base64.b64decode(configured + "=" * (-len(configured) % 4), altchars=b"-_", validate=True)
        if len(key) != 32:
            raise ValueError("Invalid key size")
        return key
    except (ValueError, TypeError):
        raise ProviderAccountError("TOKEN_ENCRYPTION_KEY harus berupa URL-safe base64 dari 32 byte acak.", 503) from None


def _account_context(user_id: int, number: int) -> bytes:
    return f"myengsel:provider-account:v1:{user_id}:{number}".encode("ascii")


def _encrypt_tokens(user_id: int, number: int, tokens: dict, key: bytes) -> str:
    cipher = AES.new(key, AES.MODE_GCM, nonce=os.urandom(12))
    cipher.update(_account_context(user_id, number))
    encrypted, tag = cipher.encrypt_and_digest(json.dumps(tokens, separators=(",", ":")).encode("utf-8"))
    return json.dumps({
        "v": 1,
        "nonce": base64.urlsafe_b64encode(cipher.nonce).decode("ascii"),
        "ciphertext": base64.urlsafe_b64encode(encrypted).decode("ascii"),
        "tag": base64.urlsafe_b64encode(tag).decode("ascii"),
    }, separators=(",", ":"))


def _decrypt_tokens(account: ProviderAccount, key: bytes) -> dict:
    try:
        envelope = json.loads(account.encrypted_tokens)
        if envelope["v"] != 1:
            raise ValueError("Unknown token format")
        cipher = AES.new(key, AES.MODE_GCM, nonce=base64.urlsafe_b64decode(envelope["nonce"]))
        cipher.update(_account_context(account.user_id, account.number))
        plaintext = cipher.decrypt_and_verify(
            base64.urlsafe_b64decode(envelope["ciphertext"]),
            base64.urlsafe_b64decode(envelope["tag"]),
        )
        tokens = json.loads(plaintext)
        if not isinstance(tokens, dict):
            raise ValueError("Invalid token payload")
        return tokens
    except (ValueError, KeyError, TypeError, UnicodeError):
        raise ProviderAccountError("Token tersimpan tidak dapat dibuka. Periksa TOKEN_ENCRYPTION_KEY di server.", 503) from None


def _check_tokens(tokens: dict) -> None:
    if not isinstance(tokens, dict) or any(
        not isinstance(tokens.get(name), str) or not tokens[name]
        for name in ("access_token", "id_token", "refresh_token")
    ):
        raise ProviderAccountError("Sesi nomor HP tidak valid atau sudah kedaluwarsa. Login OTP ulang.")


def _cache_expiry(tokens: dict) -> datetime:
    # Keep the existing five-minute cache, shortened when the provider says the
    # access token expires sooner. Expired tokens always go through refresh.
    try:
        seconds = min(300, max(0, int(tokens.get("expires_in", 330)) - 30))
    except (ValueError, TypeError, OverflowError):
        seconds = 300
    return datetime.utcnow() + timedelta(seconds=seconds)


def _active_user(account: ProviderAccount, tokens: dict) -> ActiveUser:
    return ActiveUser(
        number=account.number,
        subscriber_id=account.sub_id or "",
        subscription_type=account.sub_type or "",
        tokens=tokens,
    )


class DatabaseAuthStore:
    def __init__(self) -> None:
        self.api_key = ensure_api_key()

    @staticmethod
    def check_configuration() -> None:
        _encryption_key()

    @staticmethod
    def _owner(db, user_id: int, *, lock: bool = False) -> AppUser:
        if lock:
            owner = db.query(AppUser).filter(AppUser.id == user_id).with_for_update().first()
        else:
            owner = db.get(AppUser, user_id)
        if not owner:
            raise ProviderAccountError("Silakan login ke akun aplikasi.", 401)
        return owner

    @staticmethod
    def _metadata(db, owner: AppUser) -> list[dict]:
        accounts = db.query(ProviderAccount).filter(ProviderAccount.user_id == owner.id).order_by(ProviderAccount.id).all()
        return [{
            "number": account.number,
            "subscriber_id": account.sub_id or "",
            "subscription_type": account.sub_type or "",
            "active": account.number == owner.active_number,
        } for account in accounts]

    def list_accounts(self, user_id: int) -> list[dict]:
        init_db()
        with _account_session() as db:
            return self._metadata(db, self._owner(db, user_id))

    def add_login(self, user_id: int, number: int, tokens: dict) -> ActiveUser:
        key = _encryption_key()
        _check_tokens(tokens)
        from app.client.engsel import get_profile

        init_db()
        with _account_session() as db:
            self._owner(db, user_id)
        try:
            profile_data = get_profile(self.api_key, tokens["access_token"], tokens["id_token"])
            profile = (profile_data or {}).get("profile") or {}
        except Exception:
            # Preserve a completed OTP login even if profile enrichment fails.
            profile = {}
        encrypted_tokens = _encrypt_tokens(user_id, number, tokens, key)
        # Concurrent OTP completion may create the same owner/number pair. Retry
        # once after the uniqueness conflict, preserving the existing account.
        for attempt in range(2):
            with _account_session() as db:
                owner = self._owner(db, user_id, lock=True)
                account = db.query(ProviderAccount).filter_by(user_id=user_id, number=number).with_for_update().first()
                if account is None:
                    account = ProviderAccount(user_id=user_id, number=number)
                    db.add(account)
                account.sub_id = profile.get("subscriber_id") or account.sub_id or ""
                account.sub_type = profile.get("subscription_type") or account.sub_type or ""
                account.encrypted_tokens = encrypted_tokens
                account.expiry = _cache_expiry(tokens)
                owner.active_number = number
                result = _active_user(account, dict(tokens))
                try:
                    db.commit()
                    return result
                except IntegrityError:
                    db.rollback()
                    if attempt:
                        raise ProviderAccountError("Nomor belum dapat disimpan. Coba lagi.") from None

    def get_active(self, user_id: int, number: int | None = None) -> ActiveUser:
        key = _encryption_key()
        init_db()
        with _account_session() as db:
            owner = self._owner(db, user_id, lock=True)
            selected_number = number if number is not None else owner.active_number
            if selected_number is None:
                raise ProviderAccountError("Tambahkan nomor HP dan selesaikan login OTP terlebih dahulu.")
            account = db.query(ProviderAccount).filter_by(user_id=user_id, number=selected_number).with_for_update().first()
            if account is None:
                raise ProviderAccountError("Nomor HP tidak ditemukan di akun ini.", 404)
            tokens = _decrypt_tokens(account, key)
            _check_tokens(tokens)
            if account.expiry > datetime.utcnow():
                return _active_user(account, tokens)

            from app.client.ciam import get_new_token
            from app.client.engsel import get_profile

            try:
                refreshed = get_new_token(self.api_key, tokens["refresh_token"], account.sub_id or "")
            except Exception:
                raise ProviderAccountError("Sesi nomor HP belum dapat diperbarui. Coba lagi atau login OTP ulang.") from None
            if not isinstance(refreshed, dict):
                raise ProviderAccountError("Sesi nomor HP sudah kedaluwarsa. Login OTP ulang.")
            refreshed = dict(refreshed)
            refreshed["refresh_token"] = refreshed.get("refresh_token") or tokens["refresh_token"]
            _check_tokens(refreshed)

            # Persist a rotated refresh token even if the following profile
            # request fails, so a temporary profile error cannot lose the login.
            account.encrypted_tokens = _encrypt_tokens(user_id, selected_number, refreshed, key)
            account.expiry = _cache_expiry(refreshed)
            result = _active_user(account, refreshed)
            db.commit()
            try:
                profile_data = get_profile(self.api_key, refreshed["access_token"], refreshed["id_token"])
                profile = (profile_data or {}).get("profile") or {}
                self._owner(db, user_id, lock=True)
                account = db.query(ProviderAccount).filter_by(
                    user_id=user_id, number=selected_number,
                ).populate_existing().with_for_update().first()
                if account is None:
                    return result
                account.sub_id = profile.get("subscriber_id") or account.sub_id or ""
                account.sub_type = profile.get("subscription_type") or account.sub_type or ""
                result = _active_user(account, refreshed)
                db.commit()
            except Exception:
                db.rollback()
            return result

    def activate_account(self, user_id: int, number: int) -> list[dict]:
        init_db()
        with _account_session() as db:
            owner = self._owner(db, user_id, lock=True)
            account = db.query(ProviderAccount).filter_by(user_id=user_id, number=number).first()
            if account is None:
                raise ProviderAccountError("Nomor HP tidak ditemukan di akun ini.", 404)
            owner.active_number = number
            db.commit()
            return self._metadata(db, owner)

    def remove_account(self, user_id: int, number: int) -> list[dict]:
        init_db()
        with _account_session() as db:
            owner = self._owner(db, user_id, lock=True)
            account = db.query(ProviderAccount).filter_by(user_id=user_id, number=number).first()
            if account is None:
                raise ProviderAccountError("Nomor HP tidak ditemukan di akun ini.", 404)
            db.delete(account)
            db.flush()
            if owner.active_number == number:
                next_account = db.query(ProviderAccount).filter_by(user_id=user_id).order_by(ProviderAccount.id).first()
                owner.active_number = next_account.number if next_account else None
            db.commit()
            return self._metadata(db, owner)


AuthWeb = DatabaseAuthStore()
