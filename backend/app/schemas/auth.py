"""
認証関連のPydanticスキーマ定義

Phase A-1a: 認証API群
- JWT認証と退会管理に対応したスキーマ
- セキュリティを考慮した入力検証
"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


# =================================
# リクエストスキーマ（入力）
# =================================

class LoginRequest(BaseModel):
    """ログイン認証リクエスト

    エンドポイント: POST /api/auth/login
    """
    email: EmailStr = Field(
        ...,
        description="ログイン用メールアドレス",
        example="user@example.com"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="パスワード（8文字以上）",
        example="secure_password123"
    )


class RegistrationRequest(BaseModel):
    """ユーザー登録リクエスト

    新規アカウント作成用
    エンドポイント: POST /api/auth/register
    """
    email: EmailStr = Field(
        ...,
        description="メールアドレス",
        example="user@example.com"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="パスワード（8文字以上）",
        example="secure_password123"
    )
    business_name: Optional[str] = Field(
        None,
        max_length=100,
        description="屋号・事業者名",
        example="星の鑑定事務所"
    )
    operator_name: Optional[str] = Field(
        None,
        max_length=50,
        description="鑑定士名",
        example="山田太郎"
    )


# =================================
# レスポンススキーマ（出力）
# =================================

class LoginResponse(BaseModel):
    """ログイン認証レスポンス

    JWT認証と退会状態を含む
    """
    access_token: str = Field(
        ...,
        description="JWT アクセストークン",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    token_type: str = Field(
        default="bearer",
        description="トークンタイプ",
        example="bearer"
    )
    user_id: int = Field(
        ...,
        description="ユーザーID",
        example=1
    )
    is_superuser: bool = Field(
        ...,
        description="管理者権限フラグ",
        example=False
    )
    subscription_status: str = Field(
        ...,
        description="課金状態: active/inactive/suspended",
        example="active"
    )


class RegistrationResponse(BaseModel):
    """ユーザー登録レスポンス

    新規アカウント作成時の返却情報
    """
    success: bool = Field(
        ...,
        description="登録成功フラグ",
        example=True
    )
    message: str = Field(
        ...,
        description="登録結果メッセージ",
        example="アカウントが正常に作成されました"
    )
    user_id: int = Field(
        ...,
        description="作成されたユーザーID",
        example=1
    )
    email: str = Field(
        ...,
        description="登録されたメールアドレス",
        example="user@example.com"
    )


class UserResponse(BaseModel):
    """ユーザー情報レスポンス

    トークン検証時に返されるユーザー情報
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="ユーザーID",
        example=1
    )
    email: str = Field(
        ...,
        description="メールアドレス",
        example="user@example.com"
    )
    business_name: Optional[str] = Field(
        None,
        description="屋号・事業者名",
        example="星の鑑定事務所"
    )
    operator_name: Optional[str] = Field(
        None,
        description="鑑定士名",
        example="山田太郎"
    )
    subscription_status: str = Field(
        ...,
        description="課金状態: active/inactive/suspended",
        example="active"
    )
    is_active: bool = Field(
        ...,
        description="アカウント有効状態",
        example=True
    )
    is_superuser: bool = Field(
        ...,
        description="管理者権限フラグ",
        example=False
    )
    created_at: datetime = Field(
        ...,
        description="アカウント作成日時",
        example="2024-01-01T00:00:00Z"
    )
    updated_at: datetime = Field(
        ...,
        description="最終更新日時",
        example="2024-01-01T00:00:00Z"
    )


class MessageResponse(BaseModel):
    """一般的なメッセージレスポンス

    ログアウト等のシンプルな操作結果
    """
    success: bool = Field(
        ...,
        description="処理成功フラグ",
        example=True
    )
    message: str = Field(
        ...,
        description="処理結果メッセージ",
        example="ログアウトが完了しました"
    )


# =================================
# エラーレスポンススキーマ
# =================================

class AuthErrorResponse(BaseModel):
    """認証エラーレスポンス"""
    success: bool = Field(
        default=False,
        description="処理成功フラグ",
        example=False
    )
    error_code: str = Field(
        ...,
        description="エラーコード",
        example="INVALID_CREDENTIALS"
    )
    message: str = Field(
        ...,
        description="エラーメッセージ",
        example="メールアドレスまたはパスワードが正しくありません"
    )
    detail: Optional[str] = Field(
        None,
        description="詳細エラー情報（デバッグ用）",
        example="User not found with email: user@example.com"
    )


# =================================
# 管理者機能スキーマ
# =================================

class UserStatusUpdateRequest(BaseModel):
    """ユーザーステータス更新リクエスト（管理者専用）

    現在サブスク機能は使用していないため、is_activeとis_superuserのみ管理
    """
    is_active: Optional[bool] = Field(
        None,
        description="アカウント有効状態（退会管理）",
        example=False
    )
    is_superuser: Optional[bool] = Field(
        None,
        description="管理者権限",
        example=True
    )
    reason: Optional[str] = Field(
        None,
        description="変更理由",
        example="利用規約違反"
    )