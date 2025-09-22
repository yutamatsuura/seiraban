"""
認証サービス層

Phase S-1a: 認証サービス層実装
- JWT認証・パスワードハッシュ・セッション管理
- SQLAlchemy 2.0 準拠
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from ..models import User
from ..schemas.auth import LoginRequest, LoginResponse, UserResponse, RegistrationRequest, RegistrationResponse
from ..core.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


class AuthService:
    """認証サービス層

    JWT認証、セッション管理を担当
    """

    def __init__(self, db: Session):
        self.db = db

    def authenticate_and_login(self, credentials: LoginRequest) -> LoginResponse:
        """ログイン認証

        Args:
            credentials: ログイン情報（メール・パスワード）

        Returns:
            LoginResponse: JWT トークンとユーザー情報

        Raises:
            HTTPException: 認証失敗時
        """
        # ユーザー認証
        user = authenticate_user(self.db, credentials.email, credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="メールアドレスまたはパスワードが正しくありません"
            )

        # Note: UTAGE連携機能は削除済み
        # データベースのsubscription_status等のフィールドは維持

        # JWT トークン作成
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=int(user.id),
            is_superuser=bool(user.is_superuser),
            subscription_status=str(user.subscription_status),
            utage_user_id=str(user.utage_user_id) if user.utage_user_id else None
        )

    def verify_user_token(self, user: User) -> UserResponse:
        """トークン検証と権限確認

        Args:
            user: 認証されたユーザー（依存関数から取得）

        Returns:
            UserResponse: ユーザー詳細情報
        """
        return UserResponse.model_validate(user)

    def logout_user(self, user: User) -> Dict[str, Any]:
        """ログアウト処理

        Args:
            user: 認証されたユーザー

        Returns:
            dict: ログアウト完了メッセージ

        Note:
            JWT はステートレスなため、サーバー側では特別な処理なし
            クライアント側でトークンを削除する必要がある
            将来的にはトークンブラックリスト機能を追加予定
        """
        # TODO: 将来的にはRedisでトークンブラックリストを実装
        # 現在はクライアント側でのトークン削除に依存

        return {
            "success": True,
            "message": f"{user.email} のログアウトが完了しました"
        }

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """ユーザーIDからユーザー情報を取得

        Args:
            user_id: ユーザーID

        Returns:
            User: ユーザー情報（存在しない場合はNone）
        """
        stmt = select(User).where(
            User.id == user_id,
            User.is_active == True,
            User.deleted_at.is_(None)
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """メールアドレスからユーザー情報を取得

        Args:
            email: メールアドレス

        Returns:
            User: ユーザー情報（存在しない場合はNone）
        """
        stmt = select(User).where(
            User.email == email,
            User.is_active == True,
            User.deleted_at.is_(None)
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def update_subscription_status(self, user_id: int, status: str) -> Optional[User]:
        """課金状態の更新

        Args:
            user_id: ユーザーID
            status: 新しい課金状態 (active/inactive/suspended)

        Returns:
            User: 更新後のユーザー情報（存在しない場合はNone）
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        user.subscription_status = status  # type: ignore
        user.subscription_updated_at = datetime.now(timezone.utc)  # type: ignore
        self.db.commit()
        self.db.refresh(user)

        return user


    def check_user_permissions(self, user: User, required_subscription: str = "active") -> bool:
        """ユーザー権限チェック

        Args:
            user: ユーザー情報
            required_subscription: 必要な課金状態（デフォルト: active）

        Returns:
            bool: 権限があるかどうか
        """
        # アカウント有効性チェック
        if not user.is_active or user.deleted_at is not None:
            return False

        # 課金状態チェック
        if user.subscription_status != required_subscription:
            return False

        return True

    def register_user(self, registration_data: RegistrationRequest) -> RegistrationResponse:
        """ユーザー登録

        Args:
            registration_data: 登録情報

        Returns:
            RegistrationResponse: 登録結果

        Raises:
            HTTPException: 登録失敗時
        """
        # メールアドレス重複チェック
        existing_user = self.get_user_by_email(registration_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="このメールアドレスは既に登録されています"
            )

        # パスワードハッシュ化
        hashed_password = get_password_hash(registration_data.password)

        # 新規ユーザー作成
        new_user = User(
            email=registration_data.email,
            hashed_password=hashed_password,
            business_name=registration_data.business_name,
            operator_name=registration_data.operator_name,
            utage_user_id=registration_data.utage_user_id,
            subscription_status="active",  # デフォルトで有効
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        # データベースに保存
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return RegistrationResponse(
            success=True,
            message="アカウントが正常に作成されました",
            user_id=int(new_user.id),
            email=str(new_user.email)
        )