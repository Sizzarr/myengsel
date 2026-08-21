import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to local sqlite for development
    DATABASE_URL = "sqlite:///./local_cache.db"

# If postgresql URL starts with postgres:// or postgresql://, append pg8000 driver
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+pg8000://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TokenCache(Base):
    __tablename__ = "token_cache"
    
    number = Column(Integer, primary_key=True, index=True)
    refresh_token = Column(String(500), nullable=False)
    sub_id = Column(String(100))
    sub_type = Column(String(50))
    
    # Store token dict as JSON string
    tokens_json = Column(Text, nullable=False)
    
    # Expiry time for the cached active access token (typically short lived)
    expiry = Column(DateTime, nullable=False)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
