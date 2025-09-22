"""
データベース接続設定

SQLAlchemy 2.0 + PostgreSQL (NEON)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator

from .models import Base

# 環境変数からDATABASE_URLを取得
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# SQLAlchemy Engine作成
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("DEBUG", "False").lower() == "true"
)

# SessionLocal作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 依存関数: データベースセッション
def get_db() -> Generator[Session, None, None]:
    """FastAPI依存関数: データベースセッションを提供"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# テーブル作成（開発用）
def create_tables():
    """全テーブルを作成（alembic使用前の開発用）"""
    Base.metadata.create_all(bind=engine)


# データベース接続テスト
def test_connection() -> bool:
    """データベース接続をテスト"""
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False