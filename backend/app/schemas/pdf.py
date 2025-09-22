"""
PDF生成API群のPydanticスキーマ定義
Phase S-2b担当: 2.3, 3.1, 3.3 エンドポイント対応

仕様変更:
- メール送信機能を削除（3.2 エンドポイント削除）
- PDFダウンロード機能のみ実装

技術仕様:
- ReportLab使用
- SQLAlchemyモデル: KanteiRecord, TemplateSettings
- TemplateSettings連携（ロゴ・屋号反映）
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ===========================
# PDF生成関連スキーマ
# ===========================

class PDFGenerationRequest(BaseModel):
    """PDF鑑定書生成リクエスト"""
    kantei_record_id: int = Field(..., description="鑑定記録ID")
    custom_message: Optional[str] = Field(None, description="カスタムメッセージ", max_length=1000)
    use_template_settings: bool = Field(True, description="テンプレート設定使用フラグ")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "kantei_record_id": 123,
                "custom_message": "特別なメッセージをここに記載",
                "use_template_settings": True
            }
        }
    )


class PDFGenerationResponse(BaseModel):
    """PDF生成レスポンス"""
    success: bool = Field(..., description="生成成功フラグ")
    pdf_id: int = Field(..., description="生成されたPDF ID")
    pdf_url: str = Field(..., description="PDF URL/パス")
    file_size: int = Field(..., description="ファイルサイズ（バイト）")
    page_count: int = Field(..., description="ページ数")
    generated_at: datetime = Field(..., description="生成日時")

    model_config = ConfigDict(from_attributes=True)


class PDFPreviewResponse(BaseModel):
    """PDFプレビューレスポンス"""
    pdf_url: str = Field(..., description="PDF URL/パス")
    file_size: int = Field(..., description="ファイルサイズ（バイト）")
    page_count: int = Field(..., description="ページ数")
    client_name: str = Field(..., description="クライアント名")
    created_at: datetime = Field(..., description="作成日時")
    kantei_data: Dict[str, Any] = Field(..., description="鑑定データ")

    model_config = ConfigDict(from_attributes=True)


# ===========================
# ダウンロード関連スキーマ
# ===========================

class PDFDownloadRequest(BaseModel):
    """PDFダウンロードリクエスト"""
    kantei_record_id: int = Field(..., description="鑑定記録ID")
    download_reason: Optional[str] = Field("user_download", description="ダウンロード理由")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "kantei_record_id": 123,
                "download_reason": "user_download"
            }
        }
    )


class PDFDownloadResponse(BaseModel):
    """PDFダウンロードレスポンス"""
    success: bool = Field(..., description="ダウンロード成功フラグ")
    file_name: str = Field(..., description="ファイル名")
    file_size: int = Field(..., description="ファイルサイズ（バイト）")
    content_type: str = Field(default="application/pdf", description="コンテンツタイプ")
    download_url: str = Field(..., description="ダウンロードURL（一時的）")
    expires_at: datetime = Field(..., description="URL有効期限")

    model_config = ConfigDict(from_attributes=True)


# ===========================
# エラーレスポンス
# ===========================

class PDFErrorDetail(BaseModel):
    """PDFエラー詳細"""
    error_code: str = Field(..., description="エラーコード")
    error_message: str = Field(..., description="エラーメッセージ")
    details: Optional[Dict[str, Any]] = Field(None, description="エラー詳細情報")


class PDFErrorResponse(BaseModel):
    """PDFエラーレスポンス"""
    success: bool = Field(False, description="成功フラグ（常にFalse）")
    error: PDFErrorDetail = Field(..., description="エラー詳細")
    timestamp: datetime = Field(default_factory=datetime.now, description="エラー発生時刻")


# ===========================
# 共通レスポンス
# ===========================

class MessageResponse(BaseModel):
    """汎用メッセージレスポンス"""
    success: bool = Field(..., description="処理成功フラグ")
    message: str = Field(..., description="メッセージ")
    timestamp: datetime = Field(default_factory=datetime.now, description="レスポンス時刻")


# ===========================
# ステータス確認用スキーマ
# ===========================

class PDFStatusEnum(str, Enum):
    """PDF処理ステータス"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PDFStatusResponse(BaseModel):
    """PDF処理ステータスレスポンス"""
    kantei_record_id: int = Field(..., description="鑑定記録ID")
    pdf_status: PDFStatusEnum = Field(..., description="PDF処理ステータス")
    pdf_url: Optional[str] = Field(None, description="PDF URL（完成時）")
    error_message: Optional[str] = Field(None, description="エラーメッセージ（失敗時）")
    updated_at: datetime = Field(..., description="最終更新日時")

    model_config = ConfigDict(from_attributes=True)


# ===========================
# バリデーション関連
# ===========================

class PDFValidationRules(BaseModel):
    """PDFバリデーションルール設定"""
    max_file_size_mb: int = Field(10, description="最大ファイルサイズ（MB）")
    max_page_count: int = Field(50, description="最大ページ数")
    allowed_formats: List[str] = Field(["pdf"], description="許可フォーマット")
    generation_timeout_seconds: int = Field(30, description="生成タイムアウト（秒）")


# ===========================
# エクスポート
# ===========================

__all__ = [
    # PDF生成関連
    "PDFGenerationRequest",
    "PDFGenerationResponse",
    "PDFPreviewResponse",

    # ダウンロード関連
    "PDFDownloadRequest",
    "PDFDownloadResponse",

    # エラー・ステータス関連
    "PDFErrorResponse",
    "PDFErrorDetail",
    "PDFStatusResponse",
    "PDFStatusEnum",
    "MessageResponse",

    # バリデーション関連
    "PDFValidationRules"
]