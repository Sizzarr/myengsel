import os
import threading
from datetime import datetime
from sqlalchemy import (
    BigInteger, Column, DateTime, ForeignKey, Integer, String, Text,
    UniqueConstraint, create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    if os.environ.get("VERCEL"):
        raise RuntimeError("DATABASE_URL wajib diatur di Vercel agar akun dan sesi tersimpan permanen.")
    # Fallback to local sqlite for development
    DATABASE_URL = "sqlite:///./local_accounts.db"

# If postgresql URL starts with postgres:// or postgresql://, append pg8000 driver
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+pg8000://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
_initialized_engine = None
_init_lock = threading.Lock()

class TokenCache(Base):
    # Legacy schema reference only; never recreate it during app initialization.
    __tablename__ = "token_cache_v3"
    
    number = Column(BigInteger, primary_key=True, index=True)
    refresh_token = Column(Text, nullable=False)
    sub_id = Column(String(100))
    sub_type = Column(String(50))
    
    # Store token dict as JSON string
    tokens_json = Column(Text, nullable=False)
    
    # Expiry time for the cached active access token (typically short lived)
    expiry = Column(DateTime, nullable=False)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AppUser(Base):
    __tablename__ = "app_users"

    id = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False, unique=True, index=True)
    password_hash = Column(Text, nullable=False)
    active_number = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    failed_login_count = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime, nullable=True)


class AppSession(Base):
    __tablename__ = "app_sessions"

    token_hash = Column(String(64), primary_key=True)
    user_id = Column(Integer, ForeignKey("app_users.id"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)


class ProviderAccount(Base):
    __tablename__ = "provider_accounts"
    __table_args__ = (UniqueConstraint("user_id", "number", name="uq_provider_account_owner_number"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("app_users.id"), nullable=False, index=True)
    number = Column(BigInteger, nullable=False)
    sub_id = Column(String(100), nullable=True)
    sub_type = Column(String(50), nullable=True)
    encrypted_tokens = Column(Text, nullable=False)
    expiry = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    global _initialized_engine
    if _initialized_engine is engine:
        return
    with _init_lock:
        if _initialized_engine is not engine:
            Base.metadata.create_all(bind=engine, tables=[
                AppUser.__table__, AppSession.__table__, ProviderAccount.__table__,
            ])
            _initialized_engine = engine

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
