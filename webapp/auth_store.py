from __future__ import annotations

import time
import json
from datetime import datetime, timedelta
from dataclasses import dataclass

from app.util import ensure_api_key
from webapp.db import SessionLocal, TokenCache, init_db


@dataclass
class ActiveUser:
    number: int
    subscriber_id: str
    subscription_type: str
    tokens: dict


class StatelessAuthStore:
    """Stateless auth store for the local web UI and Vercel Deployment.
    
    Relies on the frontend to store and pass tokens (LocalStorage).
    Uses PostgreSQL (via SQLAlchemy) to cache active access_tokens for 5 minutes
    to avoid requesting new tokens on every API call.
    """

    def __init__(self) -> None:
        self.api_key = ensure_api_key()
        try:
            init_db()
        except Exception as e:
            print(f"Warning: Failed to init DB: {e}")

    def get_active(self, number: int, refresh_token: str, subscriber_id: str = "", subscription_type: str = "") -> ActiveUser:
        db = SessionLocal()
        try:
            cached = db.query(TokenCache).filter(TokenCache.number == number).first()
            if cached and cached.refresh_token == refresh_token and cached.expiry > datetime.utcnow():
                # Cache valid
                return ActiveUser(
                    number=cached.number,
                    subscriber_id=cached.sub_id or "",
                    subscription_type=cached.sub_type or "",
                    tokens=json.loads(cached.tokens_json)
                )

            # Not cached or expired, get new token
            from app.client.ciam import get_new_token
            from app.client.engsel import get_profile

            tokens = get_new_token(
                self.api_key,
                refresh_token,
                subscriber_id,
            )
            if not tokens:
                raise RuntimeError("Refresh token tidak valid atau sesi sudah kedaluwarsa.")
            
            # Ensure refresh_token is preserved if API didn't return a new one
            tokens["refresh_token"] = tokens.get("refresh_token") or refresh_token

            profile_data = get_profile(self.api_key, tokens["access_token"], tokens["id_token"])
            profile = (profile_data or {}).get("profile") or {}
            
            final_sub_id = profile.get("subscriber_id", subscriber_id)
            final_sub_type = profile.get("subscription_type", subscription_type)

            user = ActiveUser(
                number=number,
                subscriber_id=final_sub_id,
                subscription_type=final_sub_type,
                tokens=tokens,
            )
            
            if not cached:
                cached = TokenCache(number=number)
                db.add(cached)
                
            cached.refresh_token = refresh_token
            cached.sub_id = final_sub_id
            cached.sub_type = final_sub_type
            cached.tokens_json = json.dumps(tokens)
            cached.expiry = datetime.utcnow() + timedelta(minutes=5)
            
            db.commit()
            return user
        finally:
            db.close()

    def add_login(self, number: int, tokens: dict) -> ActiveUser:
        from app.client.engsel import get_profile
        
        db = SessionLocal()
        try:
            profile_data = get_profile(self.api_key, tokens["access_token"], tokens["id_token"])
            profile = (profile_data or {}).get("profile") or {}
            
            final_sub_id = profile.get("subscriber_id", "")
            final_sub_type = profile.get("subscription_type", "")
            
            cached = db.query(TokenCache).filter(TokenCache.number == number).first()
            if not cached:
                cached = TokenCache(number=number)
                db.add(cached)
                
            cached.refresh_token = tokens.get("refresh_token", "")
            cached.sub_id = final_sub_id
            cached.sub_type = final_sub_type
            cached.tokens_json = json.dumps(tokens)
            cached.expiry = datetime.utcnow() + timedelta(minutes=5)
            
            db.commit()
            
            return ActiveUser(
                number=number,
                subscriber_id=final_sub_id,
                subscription_type=final_sub_type,
                tokens=tokens,
            )
        finally:
            db.close()


AuthWeb = StatelessAuthStore()
