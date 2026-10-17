"""Account/session integration tests with an isolated DB and mocked provider."""
import base64
import hashlib
import json
import os
import secrets
import sys
import tempfile
import threading
import time
import types
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient


class AccountSessionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="myengsel-account-tests-")
        cls.env = patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///" + (Path(cls.temp.name) / "accounts.db").as_posix(),
            "TOKEN_ENCRYPTION_KEY": base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(),
            "VERCEL": "",
        })
        cls.env.start()
        cls.ciam = types.ModuleType("app.client.ciam")
        cls.engsel = types.ModuleType("app.client.engsel")
        for name in ("get_otp", "submit_otp", "get_new_token"):
            setattr(cls.ciam, name, Mock())
        for name in ("get_profile", "get_balance", "get_tiering_info", "dashboard_segments"):
            setattr(cls.engsel, name, Mock())
        cls.upstream = patch.dict(sys.modules, {
            "app.client.ciam": cls.ciam, "app.client.engsel": cls.engsel,
        })
        cls.upstream.start()
        cls.no_network = patch("requests.sessions.Session.request",
                               side_effect=AssertionError("Real provider requests are forbidden in these tests."))
        cls.no_network.start()
        from webapp import db, server
        from webapp.auth_store import AuthWeb
        from webapp.session_auth import SESSION_COOKIE
        cls.db = db
        cls.app = server.app
        cls.auth = AuthWeb
        cls.cookie_name = SESSION_COOKIE
        db.init_db()
        # Simulate an old database only for the legacy ownership regression test.
        db.TokenCache.__table__.create(bind=db.engine, checkfirst=True)

    @classmethod
    def tearDownClass(cls):
        cls.db.engine.dispose()
        cls.no_network.stop()
        cls.upstream.stop()
        cls.env.stop()
        cls.temp.cleanup()

    def setUp(self):
        with self.db.SessionLocal() as db:
            for table in reversed(self.db.Base.metadata.sorted_tables):
                db.execute(table.delete())
            db.commit()
        for module in (self.ciam, self.engsel):
            for value in vars(module).values():
                if isinstance(value, Mock):
                    value.reset_mock(return_value=True, side_effect=True)
        self.tokens = {"access_token": "test-access", "id_token": "test-id",
                       "refresh_token": "test-refresh", "expires_in": 3600}
        self.ciam.get_otp.return_value = "test-subscriber"
        self.ciam.submit_otp.return_value = dict(self.tokens)
        self.ciam.get_new_token.return_value = dict(self.tokens)
        self.engsel.get_profile.return_value = {
            "profile": {"subscriber_id": "test-subscriber", "subscription_type": "PREPAID"}}
        self.engsel.get_balance.return_value = {"remaining": 1000, "expired_at": 0}
        self.engsel.get_tiering_info.return_value = {}
        self.engsel.dashboard_segments.return_value = {}
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)

    def signup(self, client=None, username="indra", password="correct-password-123"):
        client = client or self.client
        response = client.post("/api/session/register",
                               json={"username": username, "password": password})
        self.assertEqual(response.status_code, 201, response.text)
        return response

    def link_phone(self, client=None, number="6281234567890"):
        client = client or self.client
        response = client.post("/api/auth/submit-otp", json={"number": number, "otp": "123456"})
        self.assertEqual(response.status_code, 200, response.text)
        return response

    def expire_phone(self):
        with self.db.SessionLocal() as db:
            db.query(self.db.ProviderAccount).update(
                {"expiry": datetime.utcnow() - timedelta(minutes=1)})
            db.commit()

    def test_guest_cannot_access_business_or_otp_routes(self):
        for path, body in (
            ("/api/auth/request-otp", {"number": "6281234567890"}),
            ("/api/auth/submit-otp", {"number": "6281234567890", "otp": "123456"}),
            ("/api/tools/register", {"msisdn": "6281234567890", "nik": "test", "kk": "test"}),
        ):
            self.assertEqual(self.client.post(path, json=body).status_code, 401)
        self.assertEqual(self.client.get("/api/dashboard").status_code, 401)
        self.assertEqual(self.client.get("/api/session").status_code, 401)
        self.ciam.get_otp.assert_not_called()
        self.ciam.submit_otp.assert_not_called()

    def test_registration_hashes_password_and_session_and_sets_cookie(self):
        response = self.signup(username="Indra")
        self.assertEqual(response.json()["user"]["username"], "indra")
        self.assertEqual(response.json()["accounts"], [])
        cookie = response.headers["set-cookie"].lower()
        self.assertIn("httponly", cookie)
        self.assertIn("samesite=lax", cookie)
        self.assertIn("max-age=2592000", cookie)
        self.assertEqual(response.headers["cache-control"], "no-store")
        raw_session = self.client.cookies.get(self.cookie_name)
        with self.db.SessionLocal() as db:
            user = db.query(self.db.AppUser).one()
            self.assertNotIn("correct-password-123", user.password_hash)
            self.assertTrue(user.password_hash.startswith("pbkdf2_sha256$600000$"))
            session = db.query(self.db.AppSession).one()
            self.assertEqual(session.token_hash, hashlib.sha256(raw_session.encode()).hexdigest())
            self.assertNotEqual(session.token_hash, raw_session)
        self.assertNotIn("password", response.text)

    def test_validation_duplicate_username_and_wrong_password(self):
        self.assertEqual(self.client.post("/api/session/register", json={
            "username": "invalid space", "password": "correct-password-123"}).status_code, 400)
        self.assertEqual(self.client.post("/api/session/register", json={
            "username": "indra", "password": "short"}).status_code, 400)
        self.signup()
        self.assertEqual(self.client.post("/api/session/register", json={
            "username": "INDRA", "password": "different-password-123"}).status_code, 409)
        self.assertEqual(self.client.post("/api/session/login", json={
            "username": "indra", "password": "incorrect-password-123"}).status_code, 401)

    def test_phone_tokens_encrypted_and_restored_after_new_client_and_pool(self):
        self.signup()
        linked = self.link_phone()
        self.assertNotIn("tokens", linked.json())
        self.assertNotIn("test-refresh", linked.text)
        with self.db.SessionLocal() as db:
            account = db.query(self.db.ProviderAccount).one()
            self.assertNotIn("test-refresh", account.encrypted_tokens)
            self.assertNotIn("test-access", account.encrypted_tokens)
            self.assertEqual(json.loads(account.encrypted_tokens)["v"], 1)
            self.assertEqual(db.query(self.db.TokenCache).count(), 0)
        self.db.engine.dispose()
        with TestClient(self.app) as fresh_browser:
            fresh_browser.cookies.update(self.client.cookies)
            restored = fresh_browser.get("/api/session")
            self.assertEqual(restored.status_code, 200)
            self.assertEqual(restored.json()["accounts"][0]["number"], 6281234567890)
            self.assertNotIn("refresh_token", restored.text)
            self.assertEqual(fresh_browser.get("/api/dashboard").status_code, 200)
        self.ciam.get_new_token.assert_not_called()
        self.ciam.submit_otp.assert_called_once()

    def test_logout_revokes_cookie_but_login_restores_saved_phones(self):
        self.signup()
        self.link_phone()
        previous_cookies = dict(self.client.cookies)
        self.assertEqual(self.client.post("/api/session/logout").status_code, 200)
        self.assertEqual(self.client.get("/api/session").status_code, 401)
        with TestClient(self.app) as old_browser:
            old_browser.cookies.update(previous_cookies)
            self.assertEqual(old_browser.get("/api/session").status_code, 401)
        response = self.client.post("/api/session/login", json={
            "username": "indra", "password": "correct-password-123"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(len(response.json()["accounts"]), 1)
        self.assertTrue(response.json()["accounts"][0]["active"])
        self.assertEqual(self.client.get("/api/dashboard").status_code, 200)

    def test_other_user_cannot_select_read_or_delete_saved_number(self):
        self.signup()
        self.link_phone()
        with TestClient(self.app) as other:
            self.signup(other, username="other")
            self.assertEqual(other.get("/api/accounts").json()["accounts"], [])
            response = other.get("/api/dashboard", headers={"X-Number": "6281234567890"})
            self.assertEqual(response.status_code, 404, response.text)
            self.assertEqual(other.post("/api/accounts/6281234567890/activate").status_code, 404)
            self.assertEqual(other.delete("/api/accounts/6281234567890").status_code, 404)
        self.engsel.get_balance.assert_not_called()
        self.assertEqual(len(self.client.get("/api/accounts").json()["accounts"]), 1)

    def test_same_phone_can_be_linked_independently_by_two_verified_users(self):
        self.signup()
        self.link_phone()
        with TestClient(self.app) as other:
            second_user = self.signup(other, username="other").json()["user"]["id"]
            self.ciam.submit_otp.return_value = {
                **self.tokens, "refresh_token": "second-user-refresh"}
            self.link_phone(other)
            self.assertEqual(len(other.get("/api/accounts").json()["accounts"]), 1)
        with self.db.SessionLocal() as db:
            self.assertEqual(db.query(self.db.ProviderAccount).count(), 2)
        self.assertEqual(self.auth.get_active(second_user).tokens["refresh_token"], "second-user-refresh")

    def test_expired_tokens_refresh_and_rotated_refresh_token_is_reused(self):
        user_id = self.signup().json()["user"]["id"]
        self.link_phone()
        self.expire_phone()
        self.ciam.get_new_token.return_value = {**self.tokens, "refresh_token": "rotated-refresh"}
        self.assertEqual(self.client.get("/api/dashboard").status_code, 200)
        self.assertEqual(self.ciam.get_new_token.call_args.args[1], "test-refresh")
        self.assertEqual(self.auth.get_active(user_id).tokens["refresh_token"], "rotated-refresh")
        self.expire_phone()
        self.client.get("/api/dashboard")
        self.assertEqual(self.ciam.get_new_token.call_args.args[1], "rotated-refresh")

    def test_failed_provider_refresh_keeps_saved_number_for_reauthentication(self):
        self.signup()
        self.link_phone()
        self.expire_phone()
        self.ciam.get_new_token.return_value = None
        response = self.client.get("/api/dashboard")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["code"], "provider_login_required")
        self.assertEqual(len(self.client.get("/api/accounts").json()["accounts"]), 1)

    def test_concurrent_requests_refresh_a_saved_phone_once(self):
        user_id = self.signup().json()["user"]["id"]
        self.link_phone()
        self.expire_phone()
        ready = threading.Barrier(2)

        def refresh(*args):
            time.sleep(0.05)
            return {**self.tokens, "refresh_token": "concurrent-rotation"}

        def get_active():
            ready.wait(timeout=5)
            return self.auth.get_active(user_id).tokens["refresh_token"]

        self.ciam.get_new_token.side_effect = refresh
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: get_active(), range(2)))
        self.assertEqual(results, ["concurrent-rotation", "concurrent-rotation"])
        self.ciam.get_new_token.assert_called_once()

    def test_rotated_refresh_token_survives_temporary_profile_failure(self):
        user_id = self.signup().json()["user"]["id"]
        self.link_phone()
        self.expire_phone()
        self.ciam.get_new_token.return_value = {**self.tokens, "refresh_token": "saved-before-profile"}
        self.engsel.get_profile.side_effect = RuntimeError("Temporary profile failure")
        self.assertEqual(self.client.get("/api/dashboard").status_code, 200)
        self.assertEqual(self.auth.get_active(user_id).tokens["refresh_token"], "saved-before-profile")
        self.ciam.get_new_token.assert_called_once()

    def test_missing_or_malformed_encryption_key_blocks_otp_before_provider(self):
        self.signup()
        for key in ("", "not-a-valid-32-byte-key"):
            with patch.dict(os.environ, {"TOKEN_ENCRYPTION_KEY": key}):
                response = self.client.post("/api/auth/request-otp",
                                            json={"number": "6281234567890"})
                self.assertEqual(response.status_code, 503, response.text)
        self.ciam.get_otp.assert_not_called()

    def test_cross_origin_mutations_are_rejected(self):
        body = {"username": "indra", "password": "correct-password-123"}
        self.assertEqual(self.client.post("/api/session/register", json=body,
                                         headers={"Origin": "https://foreign.invalid"}).status_code, 403)
        self.assertEqual(self.client.post("/api/session/register", json=body,
                                         headers={"Origin": "http://testserver"}).status_code, 201)
        self.assertEqual(self.client.post("/api/session/logout",
                                         headers={"Sec-Fetch-Site": "cross-site"}).status_code, 403)
        self.assertEqual(self.client.get("/api/session").status_code, 200)

    def test_expired_session_is_rejected(self):
        self.signup()
        with self.db.SessionLocal() as db:
            db.query(self.db.AppSession).update(
                {"expires_at": datetime.utcnow() - timedelta(seconds=1)})
            db.commit()
        self.assertEqual(self.client.get("/api/session").status_code, 401)
        self.assertEqual(self.client.get("/api/accounts").status_code, 401)

    def test_active_phone_switch_and_explicit_removal_persist(self):
        self.signup()
        self.link_phone(number="6281234567890")
        self.link_phone(number="6281234567891")
        response = self.client.post("/api/accounts/6281234567890/activate")
        self.assertEqual(response.status_code, 200)
        active = next(x for x in self.client.get("/api/session").json()["accounts"] if x["active"])
        self.assertEqual(active["number"], 6281234567890)
        response = self.client.delete("/api/accounts/6281234567890")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["accounts"][0]["number"], 6281234567891)
        self.assertTrue(response.json()["accounts"][0]["active"])

    def test_legacy_phone_cache_is_not_claimed_without_otp(self):
        with self.db.SessionLocal() as db:
            db.add(self.db.TokenCache(number=6281234567890, refresh_token="legacy-refresh",
                                     tokens_json=json.dumps(self.tokens),
                                     expiry=datetime.utcnow() + timedelta(minutes=5)))
            db.commit()
        self.signup()
        self.assertEqual(self.client.get("/api/accounts").json()["accounts"], [])
        self.assertEqual(self.client.get("/api/dashboard").status_code, 409)

    def test_initialization_does_not_recreate_legacy_cache(self):
        from sqlalchemy import inspect
        self.db.TokenCache.__table__.drop(bind=self.db.engine)
        try:
            self.db._initialized_engine = None
            self.db.init_db()
            names = inspect(self.db.engine).get_table_names()
            self.assertNotIn("token_cache_v3", names)
            self.assertTrue({"app_users", "app_sessions", "provider_accounts"}.issubset(names))
        finally:
            self.db.TokenCache.__table__.create(bind=self.db.engine, checkfirst=True)

    def test_secure_cookie_on_vercel(self):
        with patch.dict(os.environ, {"VERCEL": "1"}), TestClient(self.app, base_url="https://testserver") as client:
            response = self.signup(client)
            self.assertIn("; secure", response.headers["set-cookie"].lower())
            self.assertEqual(client.get("/api/session").status_code, 200)

    def test_persistent_login_throttle(self):
        self.signup()
        self.client.post("/api/session/logout")
        for _ in range(8):
            self.assertEqual(self.client.post("/api/session/login", json={
                "username": "indra", "password": "incorrect-password-123"}).status_code, 401)
        self.assertEqual(self.client.post("/api/session/login", json={
            "username": "indra", "password": "correct-password-123"}).status_code, 429)


if __name__ == "__main__":
    unittest.main()
