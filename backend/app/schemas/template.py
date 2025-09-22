"""
テンプレート設定関連のPydanticスキーマ定義

エンドポイント:
- GET /api/template/settings - テンプレート設定取得
- PUT /api/template/update - テンプレート設定更新
- POST /api/template/upload-logo - ロゴ画像アップロード

テンプレート設定のリクエスト/レスポンススキーマを定義
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class TemplateSettingsCreate(BaseModel):
    """テンプレート設定作成用スキーマ"""
    business_name: str = Field(..., max_length=255, description="屋号・事業者名")
    operator_name: str = Field(..., max_length=255, description="運営者名")
    color_theme: str = Field(default="default", max_length=50, description="カラーテーマ")
    font_family: str = Field(default="default", max_length=100, description="フォントファミリー")
    layout_style: str = Field(default="standard", max_length=50, description="レイアウトスタイル")
    custom_css: Optional[str] = Field(None, description="カスタムCSS（任意）")


class TemplateSettingsUpdate(BaseModel):
    """テンプレート設定更新用スキーマ"""
    business_name: Optional[str] = Field(None, max_length=255, description="屋号・事業者名")
    operator_name: Optional[str] = Field(None, max_length=255, description="運営者名")
    color_theme: Optional[str] = Field(None, max_length=50, description="カラーテーマ")
    font_family: Optional[str] = Field(None, max_length=100, description="フォントファミリー")
    layout_style: Optional[str] = Field(None, max_length=50, description="レイアウトスタイル")
    custom_css: Optional[str] = Field(None, description="カスタムCSS（任意）")


class TemplateSettingsResponse(BaseModel):
    """テンプレート設定レスポンス用スキーマ"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    logo_url: Optional[str] = Field(None, description="ロゴ画像URL/パス")
    logo_file_size: Optional[int] = Field(None, description="ロゴファイルサイズ（バイト）")
    business_name: str = Field(..., description="屋号・事業者名")
    operator_name: str = Field(..., description="運営者名")
    color_theme: str = Field(..., description="カラーテーマ")
    font_family: str = Field(..., description="フォントファミリー")
    layout_style: str = Field(..., description="レイアウトスタイル")
    custom_css: Optional[str] = Field(None, description="カスタムCSS（任意）")
    settings_version: str = Field(..., description="設定バージョン")
    created_at: datetime
    updated_at: datetime


class LogoUploadResponse(BaseModel):
    """ロゴアップロードレスポンス用スキーマ"""
    success: bool = Field(..., description="アップロード成功フラグ")
    logo_url: str = Field(..., description="アップロードされたロゴのURL/パス")
    file_size: int = Field(..., description="アップロードされたファイルサイズ（バイト）")
    message: str = Field(..., description="処理結果メッセージ")


class TemplateSettingsRequest(BaseModel):
    """テンプレート設定リクエスト用スキーマ（ロゴファイル以外）"""
    business_name: str = Field(..., max_length=255, description="屋号・事業者名")
    operator_name: str = Field(..., max_length=255, description="運営者名")
    color_theme: str = Field(default="default", max_length=50, description="カラーテーマ")
    font_family: str = Field(default="default", max_length=100, description="フォントファミリー")
    layout_style: str = Field(default="standard", max_length=50, description="レイアウトスタイル")
    custom_css: Optional[str] = Field(None, description="カスタムCSS（任意）")


class MessageResponse(BaseModel):
    """汎用メッセージレスポンス用スキーマ"""
    success: bool = Field(..., description="処理成功フラグ")
    message: str = Field(..., description="メッセージ")