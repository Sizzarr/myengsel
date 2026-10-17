"""Application accounts and durable opaque sessions, independent of phone login."""
from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError

from webapp.db import AppSession, AppUser, SessionLocal, init_db

SESSION_COOKIE = "myengsel_session"
SESSION_MAX_AGE = 30 * 86400
_PASSWORD_ITERATIONS = 600_000
_USERNAME_PATTERN = re.compile(r"[A-Za-z0-9_.-]{3,32}", re.ASCII)
_INVALID_CREDENTIALS = "Username atau password salah."
_DUMMY_SALT = b"myengsel-dummy-password-check"


class AccountAuthError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _normalize_username(username: str) -> str:
    username = username.strip() if isinstance(username, str) else ""
    if not _USERNAME_PATTERN.fullmatch(username):
        raise AccountAuthError("Username harus 3–32 karakter: huruf, angka, titik, garis bawah, atau tanda minus.")
    return username.lower()


def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PASSWORD_ITERATIONS)
    return "$".join((
        "pbkdf2_sha256", str(_PASSWORD_ITERATIONS),
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    ))


def _verify_password(password: str, encoded: str | None) -> bool:
    if encoded:
        try:
            algorithm, iterations, salt, expected = encoded.split("$")
            iterations = int(iterations)
            if algorithm != "pbkdf2_sha256" or not 100_000 <= iterations <= 2_000_000:
                return False
            salt_bytes = base64.b64decode(salt, altchars=b"-_", validate=True)
            expected_bytes = base64.b64decode(expected, altchars=b"-_", validate=True)
            digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, iterations)
            return hmac.compare_digest(digest, expected_bytes)
        except (ValueError, TypeError):
            return False
    # Unknown usernames still perform the same expensive password derivation.
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), _DUMMY_SALT, _PASSWORD_ITERATIONS)
    hmac.compare_digest(digest, bytes(32))
    return False


def _user_dict(user: AppUser) -> dict:
    return {"id": user.id, "username": user.username}


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class ApplicationAuthStore:
    @staticmethod
    def _new_session(db, user_id: int) -> str:
        token = secrets.token_urlsafe(32)
        db.add(AppSession(
            token_hash=_token_hash(token), user_id=user_id,
            expires_at=datetime.utcnow() + timedelta(seconds=SESSION_MAX_AGE),
        ))
        return token

    def register(self, username: str, password: str) -> tuple[dict, str]:
        username = _normalize_username(username)
        if not isinstance(password, str) or not 10 <= len(password) <= 128:
            raise AccountAuthError("Password harus 10–128 karakter.")
        password_hash = _hash_password(password)
        init_db()
        with SessionLocal() as db:
            user = AppUser(username=username, password_hash=password_hash)
            db.add(user)
            try:
                db.flush()
                token = self._new_session(db, user.id)
                result = _user_dict(user)
                db.commit()
            except IntegrityError:
                db.rollback()
                raise AccountAuthError("Username sudah dipakai. Pilih username lain.", 409) from None
            return result, token

    def login(self, username: str, password: str) -> tuple[dict, str]:
        try:
            username = _normalize_username(username)
        except AccountAuthError:
            raise AccountAuthError(_INVALID_CREDENTIALS, 401) from None
        if not isinstance(password, str) or not 10 <= len(password) <= 128:
            raise AccountAuthError(_INVALID_CREDENTIALS, 401)
        init_db()
        with SessionLocal() as db:
            user = db.query(AppUser).filter(AppUser.username == username).with_for_update().first()
            now = datetime.utcnow()
            if user and user.locked_until and user.locked_until > now:
                raise AccountAuthError("Terlalu banyak percobaan login. Coba lagi dalam 15 menit.", 429)
            if not _verify_password(password, user.password_hash if user else None):
                if user:
                    user.failed_login_count = (user.failed_login_count or 0) + 1
                    if user.failed_login_count >= 8:
                        user.locked_until = now + timedelta(minutes=15)
                        user.failed_login_count = 0
                    db.commit()
                raise AccountAuthError(_INVALID_CREDENTIALS, 401)
            user.failed_login_count = 0
            user.locked_until = None
            token = self._new_session(db, user.id)
            result = _user_dict(user)
            db.commit()
            return result, token

    def get_user(self, token: str | None) -> dict | None:
        if not isinstance(token, str) or not 32 <= len(token) <= 128:
            return None
        init_db()
        with SessionLocal() as db:
            session = db.get(AppSession, _token_hash(token))
            if session is None:
                return None
            if session.expires_at <= datetime.utcnow():
                db.delete(session)
                db.commit()
                return None
            user = db.get(AppUser, session.user_id)
            return _user_dict(user) if user else None

    def logout(self, token: str | None) -> None:
        if not isinstance(token, str) or not 32 <= len(token) <= 128:
            return
        init_db()
        with SessionLocal() as db:
            session = db.get(AppSession, _token_hash(token))
            if session:
                db.delete(session)
                db.commit()


AppAuth = ApplicationAuthStore()
