"""
認証関連の依存関数

JWT認証・ユーザー取得・権限確認
"""

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional

from ...database import get_db
from ...models import User
from ...core.security import get_current_user_id_from_token


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """現在のユーザーを取得（JWT認証）

    Args:
        authorization: Bearer トークン
        db: データベースセッション

    Returns:
        User: 認証されたユーザー

    Raises:
        HTTPException: 認証失敗時
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が無効です",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if authorization is None:
        raise credentials_exception

    # Bearer トークンの形式チェック
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    # JWTトークンからユーザーID取得
    user_id = get_current_user_id_from_token(token)
    if user_id is None:
        raise credentials_exception

    # データベースからユーザー取得
    from sqlalchemy import select

    stmt = select(User).where(
        User.id == user_id,
        User.is_active == True,
        User.deleted_at.is_(None)
    )
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


def get_optional_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """オプショナルなユーザー取得（認証なしでもOK）

    Args:
        authorization: Bearer トークン（任意）
        db: データベースセッション

    Returns:
        Optional[User]: 認証されたユーザーまたはNone
    """
    if authorization is None:
        return None

    try:
        return get_current_user(authorization, db)
    except HTTPException:
        return None


def verify_active_subscription(current_user: User = Depends(get_current_user)) -> User:
    """有効な課金状態を確認

    Args:
        current_user: 現在のユーザー

    Returns:
        User: 課金状態が有効なユーザー

    Raises:
        HTTPException: 課金状態が無効時
    """
    if current_user.subscription_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="有効な課金プランが必要です"
        )

    return current_user


def verify_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """管理者権限を確認

    Args:
        current_user: 現在のユーザー

    Returns:
        User: 管理者権限を持つユーザー

    Raises:
        HTTPException: 管理者権限がない時
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です"
        )

    return current_user


def verify_admin_or_owner(current_user: User = Depends(get_current_user)):
    """管理者権限または所有者権限を確認する依存関数ファクトリ

    Args:
        current_user: 現在のユーザー

    Returns:
        function: 所有者確認を行う関数
    """
    def check_owner_or_admin(resource_user_id: int):
        """リソースの所有者または管理者かを確認"""
        if current_user.is_superuser or current_user.id == resource_user_id:
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このリソースにアクセスする権限がありません"
        )

    return check_owner_or_admin