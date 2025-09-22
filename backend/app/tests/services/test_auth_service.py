"""
認証サービス層の単体テスト

Phase S-1a: 認証サービス層実装
- 実データ主義（モック禁止）
- .env.localのPostgreSQL使用
- 依存性注入フィクスチャ活用
"""

import pytest
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ...services.auth_service import AuthService
from ...schemas.auth import LoginRequest, LoginResponse, UserResponse
from ...models import User
from ...core.security import get_password_hash


class TestAuthService:
    """認証サービス層のテストクラス"""

    @pytest.mark.asyncio
    async def test_authenticate_and_login_success(
        self,
        auth_service: AuthService,
        test_user: User,
        login_request_data: dict
    ):
        """正常なログイン認証テスト"""
        # ログインリクエスト作成
        credentials = LoginRequest(**login_request_data)

        # ログイン実行
        result = await auth_service.authenticate_and_login(credentials)

        # 検証
        assert isinstance(result, LoginResponse)
        assert result.access_token is not None
        assert result.token_type == "bearer"
        assert result.user_id == test_user.id
        assert result.subscription_status == test_user.subscription_status
        assert result.utage_user_id == test_user.utage_user_id

    @pytest.mark.asyncio
    async def test_authenticate_and_login_invalid_email(
        self,
        auth_service: AuthService
    ):
        """存在しないメールアドレスでのログイン失敗テスト"""
        # 存在しないメールアドレス
        credentials = LoginRequest(
            email="nonexistent@example.com",
            password="any_password"
        )

        # ログイン実行（失敗）
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate_and_login(credentials)

        # エラー検証
        assert exc_info.value.status_code == 401
        assert "メールアドレスまたはパスワードが正しくありません" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_authenticate_and_login_invalid_password(
        self,
        auth_service: AuthService,
        test_user: User,
        test_user_data: dict
    ):
        """間違ったパスワードでのログイン失敗テスト"""
        # 間違ったパスワード
        credentials = LoginRequest(
            email=test_user_data["email"],
            password="wrong_password"
        )

        # ログイン実行（失敗）
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate_and_login(credentials)

        # エラー検証
        assert exc_info.value.status_code == 401
        assert "メールアドレスまたはパスワードが正しくありません" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_authenticate_and_login_inactive_user(
        self,
        auth_service: AuthService,
        inactive_user: User,
        test_user_data: dict
    ):
        """非アクティブユーザーでのログイン失敗テスト"""
        # 非アクティブユーザーのメールアドレス
        credentials = LoginRequest(
            email=inactive_user.email,
            password=test_user_data["password"]
        )

        # ログイン実行（失敗）
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate_and_login(credentials)

        # エラー検証
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_verify_user_token(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """トークン検証テスト"""
        # トークン検証実行
        result = await auth_service.verify_user_token(test_user)

        # 検証
        assert isinstance(result, UserResponse)
        assert result.id == test_user.id
        assert result.email == test_user.email
        assert result.business_name == test_user.business_name
        assert result.operator_name == test_user.operator_name
        assert result.subscription_status == test_user.subscription_status
        assert result.is_active == test_user.is_active

    @pytest.mark.asyncio
    async def test_logout_user(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """ログアウト処理テスト"""
        # ログアウト実行
        result = await auth_service.logout_user(test_user)

        # 検証
        assert isinstance(result, dict)
        assert result["success"] is True
        assert test_user.email in result["message"]
        assert "ログアウトが完了しました" in result["message"]

    @pytest.mark.asyncio
    async def test_get_user_by_id_exists(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """ユーザーID検索（存在）テスト"""
        # ユーザー検索実行
        result = await auth_service.get_user_by_id(test_user.id)

        # 検証
        assert result is not None
        assert result.id == test_user.id
        assert result.email == test_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_exists(
        self,
        auth_service: AuthService
    ):
        """ユーザーID検索（存在しない）テスト"""
        # 存在しないユーザーID
        non_existent_id = 99999999

        # ユーザー検索実行
        result = await auth_service.get_user_by_id(non_existent_id)

        # 検証
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_email_exists(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """メールアドレス検索（存在）テスト"""
        # ユーザー検索実行
        result = await auth_service.get_user_by_email(test_user.email)

        # 検証
        assert result is not None
        assert result.id == test_user.id
        assert result.email == test_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_exists(
        self,
        auth_service: AuthService
    ):
        """メールアドレス検索（存在しない）テスト"""
        # 存在しないメールアドレス
        non_existent_email = "nonexistent@example.com"

        # ユーザー検索実行
        result = await auth_service.get_user_by_email(non_existent_email)

        # 検証
        assert result is None

    @pytest.mark.asyncio
    async def test_update_subscription_status_success(
        self,
        auth_service: AuthService,
        test_user: User,
        db_session: Session
    ):
        """課金状態更新（成功）テスト"""
        # 更新前の状態を記録
        original_status = test_user.subscription_status

        # 課金状態更新実行
        new_status = "suspended"
        result = await auth_service.update_subscription_status(test_user.id, new_status)

        # 検証
        assert result is not None
        assert result.id == test_user.id
        assert result.subscription_status == new_status
        assert result.subscription_updated_at is not None

        # データベースの状態も確認
        db_session.refresh(test_user)
        assert test_user.subscription_status == new_status

    @pytest.mark.asyncio
    async def test_update_subscription_status_user_not_found(
        self,
        auth_service: AuthService
    ):
        """課金状態更新（ユーザー存在しない）テスト"""
        # 存在しないユーザーID
        non_existent_id = 99999999

        # 課金状態更新実行
        result = await auth_service.update_subscription_status(non_existent_id, "active")

        # 検証
        assert result is None

    @pytest.mark.asyncio
    async def test_verify_utage_integration(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """UTAGE連携確認テスト（モック実装）"""
        # UTAGE連携確認実行
        result = await auth_service.verify_utage_integration(test_user.utage_user_id)

        # 検証（現在はモック実装）
        assert result.utage_user_id == test_user.utage_user_id
        assert result.subscription_status == "active"  # モックでは常にactive
        assert result.webhook_verified is True
        assert result.subscription_updated_at is not None

    @pytest.mark.asyncio
    async def test_check_user_permissions_active_user(
        self,
        auth_service: AuthService,
        test_user: User
    ):
        """ユーザー権限チェック（有効ユーザー）テスト"""
        # 権限チェック実行
        result = await auth_service.check_user_permissions(test_user, "active")

        # 検証
        assert result is True

    @pytest.mark.asyncio
    async def test_check_user_permissions_inactive_subscription(
        self,
        auth_service: AuthService,
        suspended_user: User
    ):
        """ユーザー権限チェック（課金停止）テスト"""
        # 権限チェック実行（activeが必要）
        result = await auth_service.check_user_permissions(suspended_user, "active")

        # 検証
        assert result is False

    @pytest.mark.asyncio
    async def test_check_user_permissions_inactive_user(
        self,
        auth_service: AuthService,
        inactive_user: User
    ):
        """ユーザー権限チェック（非アクティブユーザー）テスト"""
        # 権限チェック実行
        result = await auth_service.check_user_permissions(inactive_user, "active")

        # 検証
        assert result is False