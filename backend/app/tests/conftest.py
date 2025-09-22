"""
テスト用設定

実データテスト環境:
- .env.localのPostgreSQLデータベースを使用
- 実際のサービス層を使用
- モック禁止のテスト実行
"""

import pytest
import os
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from dotenv import load_dotenv

# 環境変数を.env.localから読込
load_dotenv()

from ..database import get_db
from ..models import Base, User
from ..services.auth_service import AuthService
from ..core.security import get_password_hash


# データベース設定
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URLが.env.localに設定されていません")

# SQLAlchemyエンジンとセッション設定
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """データベースエンジン提供"""
    return engine


@pytest.fixture(scope="function")
def db_session(db_engine):
    """データベースセッション提供（テスト用スコープ）"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def auth_service(db_session):
    """認証サービス層のテスト用インスタンス"""
    return AuthService(db_session)


@pytest.fixture(scope="function")
def test_user_data():
    """テスト用ユーザーデータ"""
    return {
        "email": f"test.user.{datetime.now().timestamp()}@example.com",
        "password": "test_password_123",
        "business_name": "テストサロン",
        "operator_name": "テスト太郎",
        "utage_user_id": f"utage_test_{datetime.now().timestamp()}"
    }


@pytest.fixture(scope="function")
def test_user(db_session, test_user_data):
    """実際のテストユーザーをデータベースに作成"""
    user = User(
        email=test_user_data["email"],
        hashed_password=get_password_hash(test_user_data["password"]),
        business_name=test_user_data["business_name"],
        operator_name=test_user_data["operator_name"],
        utage_user_id=test_user_data["utage_user_id"],
        subscription_status="active",
        is_active=True
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    yield user

    # テスト後のクリーンアップ
    user.deleted_at = datetime.utcnow()
    user.is_active = False
    db_session.commit()


@pytest.fixture(scope="function")
def inactive_user(db_session, test_user_data):
    """非アクティブテストユーザー"""
    user_data = test_user_data.copy()
    user_data["email"] = f"inactive.{user_data['email']}"

    user = User(
        email=user_data["email"],
        hashed_password=get_password_hash(user_data["password"]),
        business_name=user_data["business_name"],
        operator_name=user_data["operator_name"],
        subscription_status="inactive",
        is_active=False
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    yield user

    # クリーンアップ
    user.deleted_at = datetime.utcnow()
    db_session.commit()


@pytest.fixture(scope="function")
def suspended_user(db_session, test_user_data):
    """停止中テストユーザー"""
    user_data = test_user_data.copy()
    user_data["email"] = f"suspended.{user_data['email']}"

    user = User(
        email=user_data["email"],
        hashed_password=get_password_hash(user_data["password"]),
        business_name=user_data["business_name"],
        operator_name=user_data["operator_name"],
        subscription_status="suspended",
        is_active=True
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    yield user

    # クリーンアップ
    user.deleted_at = datetime.utcnow()
    user.is_active = False
    db_session.commit()


@pytest.fixture
def login_request_data(test_user_data):
    """ログインリクエストデータ"""
    return {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }


# ヘルパー関数（テスト用ユーティリティ）
def create_temp_user(db_session: Session, email_suffix: str = None) -> User:
    """テスト用一時ユーザー作成ヘルパー"""
    timestamp = datetime.now().timestamp()
    email_suffix = email_suffix or "temp"

    user = User(
        email=f"temp.{email_suffix}.{timestamp}@example.com",
        hashed_password=get_password_hash("temp_password_123"),
        business_name="一時サロン",
        operator_name="一時太郎",
        subscription_status="active",
        is_active=True
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def cleanup_test_user(db_session: Session, user: User):
    """テストユーザーのクリーンアップヘルパー"""
    user.deleted_at = datetime.utcnow()
    user.is_active = False
    db_session.commit()