"""
セキュリティ関連の処理

JWT認証・パスワードハッシュ化
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..models import User

# JWT設定
SECRET_KEY = os.getenv("SECRET_KEY", "dev-super-secret-key-kantei-system-v2-local")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# パスワードハッシュ化
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワード検証"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """パスワードハッシュ化"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """JWT アクセストークン作成"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """JWT トークン検証"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """ユーザー認証（メール・パスワード）

    SQLAlchemy 2.0準拠のクエリ実装
    """
    from sqlalchemy import select

    stmt = select(User).where(
        User.email == email,
        User.is_active == True,
        User.deleted_at.is_(None)
    )
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return None

    if not verify_password(password, str(user.hashed_password)):
        return None

    return user




def get_current_user_id_from_token(token: str) -> Optional[int]:
    """JWTトークンからユーザーIDを取得"""
    payload = verify_token(token)
    if payload is None:
        return None

    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        return None

    return int(user_id)