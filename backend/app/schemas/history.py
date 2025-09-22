"""
履歴管理API用のPydanticスキーマ定義

Phase A-3a: 履歴管理API群
- 4.1 `/api/kantei/history` GET - 鑑定履歴一覧取得
- 4.2 `/api/kantei/detail/{id}` GET - 鑑定詳細情報取得
- 4.3 `/api/kantei/resend/{id}` POST - 鑑定書再送信

技術仕様:
- SQLAlchemyモデル: KanteiRecord, EmailHistory（作成済み）
- ページネーション機能
- P-004モックアップ準拠
"""

from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# =========================================
# 列挙型定義
# =========================================

class KanteiStatus(str, Enum):
    """鑑定記録のステータス"""
    CREATED = "created"        # 作成済み
    PROCESSING = "processing"  # 処理中
    COMPLETED = "completed"    # 完了
    FAILED = "failed"         # 失敗


class EmailStatus(str, Enum):
    """メール送信ステータス"""
    PENDING = "pending"   # 送信待ち
    SENT = "sent"        # 送信済み
    FAILED = "failed"    # 送信失敗
    BOUNCED = "bounced"  # バウンス


# =========================================
# 基本スキーマ
# =========================================

class EmailHistoryBase(BaseModel):
    """メール履歴基本スキーマ"""
    recipient_email: EmailStr = Field(..., description="送信先メールアドレス")
    sender_name: Optional[str] = Field(None, description="送信者名")
    subject: str = Field(..., description="メール件名")
    message_content: Optional[str] = Field(None, description="メール本文")
    status: EmailStatus = Field(EmailStatus.PENDING, description="送信ステータス")


class EmailHistoryResponse(EmailHistoryBase):
    """メール履歴レスポンス"""
    id: int = Field(..., description="メール履歴ID")
    kantei_record_id: int = Field(..., description="鑑定記録ID")
    message_id: Optional[str] = Field(None, description="送信サービスのメッセージID")
    provider: Optional[str] = Field(None, description="送信プロバイダー")
    error_message: Optional[str] = Field(None, description="エラー詳細")
    sent_at: Optional[datetime] = Field(None, description="送信実行時刻")
    delivered_at: Optional[datetime] = Field(None, description="配信確認時刻")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = ConfigDict(from_attributes=True)


# =========================================
# 鑑定履歴一覧API (4.1)
# =========================================

class KanteiHistoryItem(BaseModel):
    """鑑定履歴一覧項目"""
    id: int = Field(..., description="鑑定記録ID")
    client_name: str = Field(..., description="クライアント氏名")
    client_email: Optional[str] = Field(None, description="クライアントメールアドレス")
    status: KanteiStatus = Field(..., description="鑑定ステータス")
    custom_message: Optional[str] = Field(None, description="カスタムメッセージ")
    pdf_url: Optional[str] = Field(None, description="PDF URL")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    # メール送信関連統計
    email_count: int = Field(0, description="メール送信回数")
    last_sent_at: Optional[datetime] = Field(None, description="最終送信日時")

    model_config = ConfigDict(from_attributes=True)


class KanteiHistoryResponse(BaseModel):
    """鑑定履歴一覧レスポンス"""
    total: int = Field(..., description="総件数", ge=0)
    page: int = Field(..., description="現在のページ番号", ge=1)
    limit: int = Field(..., description="1ページあたりの件数", ge=1, le=100)
    total_pages: int = Field(..., description="総ページ数", ge=1)
    items: List[KanteiHistoryItem] = Field(..., description="鑑定履歴一覧")

    model_config = ConfigDict(from_attributes=True)


# =========================================
# 鑑定詳細情報API (4.2)
# =========================================

class KanteiDetailResponse(BaseModel):
    """鑑定詳細情報レスポンス"""
    id: int = Field(..., description="鑑定記録ID")
    user_id: int = Field(..., description="ユーザーID")

    # クライアント情報
    client_name: str = Field(..., description="クライアント氏名")
    client_email: Optional[str] = Field(None, description="クライアントメールアドレス")
    client_info: Dict[str, Any] = Field(..., description="クライアント詳細情報（JSON）")

    # 鑑定データ
    calculation_result: Dict[str, Any] = Field(..., description="鑑定計算結果（JSON）")

    # PDF関連
    pdf_url: Optional[str] = Field(None, description="PDF URL")
    pdf_file_size: Optional[int] = Field(None, description="PDFファイルサイズ（バイト）")
    pdf_generated_at: Optional[datetime] = Field(None, description="PDF生成日時")

    # 状態管理
    status: KanteiStatus = Field(..., description="鑑定ステータス")
    custom_message: Optional[str] = Field(None, description="カスタムメッセージ")

    # タイムスタンプ
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    # メール送信履歴
    email_history: List[EmailHistoryResponse] = Field([], description="メール送信履歴")

    model_config = ConfigDict(from_attributes=True)


# =========================================
# 鑑定書再送信API (4.3)
# =========================================

class ResendRequest(BaseModel):
    """鑑定書再送信リクエスト"""
    recipient_email: EmailStr = Field(..., description="送信先メールアドレス")
    sender_name: Optional[str] = Field(None, description="送信者名（任意）")
    message: Optional[str] = Field(None, description="追加メッセージ（任意）", max_length=1000)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )


class ResendResponse(BaseModel):
    """鑑定書再送信レスポンス"""
    success: bool = Field(..., description="送信成功フラグ")
    message: str = Field(..., description="結果メッセージ")
    email_history_id: Optional[int] = Field(None, description="作成されたメール履歴ID")
    message_id: Optional[str] = Field(None, description="送信サービスのメッセージID")
    sent_at: Optional[datetime] = Field(None, description="送信実行時刻")

    model_config = ConfigDict(from_attributes=True)


# =========================================
# 共通レスポンス
# =========================================

class MessageResponse(BaseModel):
    """汎用メッセージレスポンス"""
    message: str = Field(..., description="メッセージ")
    success: bool = Field(True, description="成功フラグ")


class ErrorResponse(BaseModel):
    """エラーレスポンス"""
    detail: str = Field(..., description="エラー詳細")
    error_code: Optional[str] = Field(None, description="エラーコード")


# =========================================
# バリデーション関数
# =========================================

def validate_pagination_params(page: int, limit: int) -> tuple[int, int]:
    """ページネーションパラメータのバリデーション"""
    if page < 1:
        page = 1
    if limit < 1:
        limit = 20
    elif limit > 100:
        limit = 100

    return page, limit


def calculate_offset(page: int, limit: int) -> int:
    """オフセット計算"""
    return (page - 1) * limit


def calculate_total_pages(total: int, limit: int) -> int:
    """総ページ数計算"""
    return (total + limit - 1) // limit