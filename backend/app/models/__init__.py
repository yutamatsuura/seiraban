"""
SQLAlchemyモデル定義 - 鑑定システムv2
単一真実源として全てのDBモデルをここに集約

技術スタック: SQLAlchemy 2.0 + PostgreSQL (NEON) + FastAPI
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

Base = declarative_base()

# =========================================
# 認証関連モデル
# =========================================

class User(Base):
    """ユーザー（鑑定士）モデル

    UTAGE課金連携対応:
    - utage_user_id: UTAGE システムとの連携ID
    - subscription_status: 課金状態の管理

    セキュリティ:
    - hashed_password: bcryptによるハッシュ化パスワード
    - is_active: アカウント有効/無効制御
    - deleted_at: 論理削除対応
    """
    __tablename__ = "users"

    # 基本情報
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False, comment="ログイン用メールアドレス")
    hashed_password = Column(String(255), nullable=False, comment="bcryptハッシュ化パスワード（内部のみ）")

    # プロファイル情報
    business_name = Column(String(255), nullable=True, comment="屋号・事業者名")
    operator_name = Column(String(255), nullable=True, comment="鑑定士名")

    # 認証・権限
    is_active = Column(Boolean, default=True, nullable=False, comment="アカウント有効状態")
    is_superuser = Column(Boolean, default=False, nullable=False, comment="管理者権限")

    # UTAGE課金連携（一時的に戻す - 実際のDBスキーマに合わせる）
    utage_user_id = Column(String(255), nullable=True, comment="UTAGE ユーザーID")
    subscription_status = Column(String(50), default="active", nullable=False, comment="課金状態: active/inactive/suspended")
    subscription_updated_at = Column(DateTime, nullable=True, comment="課金状態更新日時")

    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True, comment="論理削除日時")

    # リレーション
    kantei_records = relationship("KanteiRecord", back_populates="user", cascade="all, delete-orphan")
    template_settings = relationship("TemplateSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")

    # インデックス
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
        Index('idx_user_subscription_status', 'subscription_status'),
        Index('idx_user_created_at', 'created_at'),
    )

# =========================================
# 鑑定関連モデル
# =========================================

class KanteiRecord(Base):
    """鑑定記録モデル

    九星気学・姓名判断・吉方位の統合鑑定結果を保存

    データ構造:
    - client_info: クライアント基本情報（JSON）
    - calculation_result: 鑑定計算結果（JSON）
    - pdf_metadata: PDF生成関連メタデータ
    """
    __tablename__ = "kantei_records"

    # 基本情報
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # クライアント情報
    client_name = Column(String(255), nullable=False, index=True, comment="クライアント氏名")
    client_email = Column(String(255), nullable=True, comment="クライアントメールアドレス")

    # 鑑定データ（JSON保存）
    client_info = Column(JSON, nullable=False, comment="""
    クライアント詳細情報: {
        "name": "氏名",
        "birth_date": "生年月日",
        "birth_time": "出生時刻（任意）",
        "gender": "性別",
        "birth_place": "出生地（任意）"
    }
    """)

    calculation_result = Column(JSON, nullable=False, comment="""
    鑑定計算結果: {
        "kyusei_kigaku": {...},    # 九星気学結果
        "seimei_handan": {...},    # 姓名判断結果
        "kichihoui": {...},        # 吉方位結果
        "template_ids": [...]      # 使用テンプレートID一覧
    }
    """)

    # PDF関連
    pdf_url = Column(String(500), nullable=True, comment="生成PDFのURL/パス")
    pdf_file_size = Column(Integer, nullable=True, comment="PDFファイルサイズ（バイト）")
    pdf_generated_at = Column(DateTime, nullable=True, comment="PDF生成日時")

    # 状態管理
    status = Column(String(50), default="created", nullable=False, comment="状態: created/processing/completed/failed")
    custom_message = Column(Text, nullable=True, comment="カスタムメッセージ")

    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True, comment="論理削除日時")

    # リレーション
    user = relationship("User", back_populates="kantei_records")
    email_history = relationship("EmailHistory", back_populates="kantei_record", cascade="all, delete-orphan")

    # インデックス
    __table_args__ = (
        Index('idx_kantei_user_created', 'user_id', 'created_at'),
        Index('idx_kantei_client_name', 'client_name'),
        Index('idx_kantei_status', 'status'),
        Index('idx_kantei_created_at', 'created_at'),
    )

class EmailHistory(Base):
    """メール送信履歴モデル

    PDF鑑定書の送信履歴を詳細に記録

    機能:
    - 送信成功/失敗の追跡
    - 再送信機能のサポート
    - メール配信サービス（SendGrid等）の連携
    """
    __tablename__ = "email_history"

    # 基本情報
    id = Column(Integer, primary_key=True, index=True)
    kantei_record_id = Column(Integer, ForeignKey("kantei_records.id"), nullable=False, index=True)

    # 送信情報
    recipient_email = Column(String(255), nullable=False, index=True, comment="送信先メールアドレス")
    sender_name = Column(String(255), nullable=True, comment="送信者名（カスタマイズ用）")
    subject = Column(String(500), nullable=False, comment="メール件名")
    message_content = Column(Text, nullable=True, comment="メール本文")

    # 配信サービス連携
    message_id = Column(String(255), nullable=True, index=True, comment="送信サービスのメッセージID")
    provider = Column(String(50), nullable=True, comment="送信プロバイダー: sendgrid/mailgun等")

    # 状態管理
    status = Column(String(50), default="pending", nullable=False, comment="状態: pending/sent/failed/bounced")
    error_message = Column(Text, nullable=True, comment="エラー詳細（失敗時）")

    # タイムスタンプ
    sent_at = Column(DateTime, nullable=True, comment="送信実行時刻")
    delivered_at = Column(DateTime, nullable=True, comment="配信確認時刻")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # リレーション
    kantei_record = relationship("KanteiRecord", back_populates="email_history")

    # インデックス
    __table_args__ = (
        Index('idx_email_kantei_sent', 'kantei_record_id', 'sent_at'),
        Index('idx_email_recipient', 'recipient_email'),
        Index('idx_email_status', 'status'),
        Index('idx_email_message_id', 'message_id'),
    )

# =========================================
# 設定・カスタマイズ関連モデル
# =========================================

class TemplateSettings(Base):
    """テンプレート設定モデル

    鑑定書のブランディング・デザインカスタマイズ

    機能:
    - ロゴ画像の管理
    - 色・フォントテーマ設定
    - レイアウトカスタマイズ
    """
    __tablename__ = "template_settings"

    # 基本情報
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # ブランディング
    logo_url = Column(String(500), nullable=True, comment="ロゴ画像URL/パス")
    logo_file_size = Column(Integer, nullable=True, comment="ロゴファイルサイズ（バイト）")
    business_name = Column(String(255), nullable=False, comment="屋号・事業者名")
    operator_name = Column(String(255), nullable=False, comment="運営者名")

    # デザイン設定
    color_theme = Column(String(50), default="default", nullable=False, comment="カラーテーマ: default/blue/green/purple等")
    font_family = Column(String(100), default="default", nullable=False, comment="フォントファミリー")
    layout_style = Column(String(50), default="standard", nullable=False, comment="レイアウトスタイル")

    # カスタムCSS（上級者向け）
    custom_css = Column(Text, nullable=True, comment="カスタムCSS（任意）")

    # 設定メタデータ
    settings_version = Column(String(20), default="1.0", nullable=False, comment="設定バージョン")

    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # リレーション
    user = relationship("User", back_populates="template_settings")

    # インデックス
    __table_args__ = (
        Index('idx_template_user', 'user_id'),
        Index('idx_template_updated', 'updated_at'),
    )

# =========================================
# システム管理関連モデル
# =========================================

class SystemSettings(Base):
    """システム設定モデル

    アプリケーション全体の設定管理

    機能:
    - 外部API設定（UTAGE, メール送信等）
    - システム制限値の管理
    - 機能フラグ管理
    """
    __tablename__ = "system_settings"

    # 基本情報
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), unique=True, nullable=False, index=True, comment="設定キー")
    setting_value = Column(Text, nullable=True, comment="設定値（JSON可）")

    # メタデータ
    description = Column(Text, nullable=True, comment="設定の説明")
    setting_type = Column(String(50), default="string", nullable=False, comment="値の型: string/json/boolean/number")
    is_public = Column(Boolean, default=False, nullable=False, comment="公開設定（フロントエンドアクセス可否）")

    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # インデックス
    __table_args__ = (
        Index('idx_system_key', 'setting_key'),
        Index('idx_system_public', 'is_public'),
    )

class AuditLog(Base):
    """監査ログモデル

    重要な操作の記録・追跡

    機能:
    - ユーザー操作の記録
    - データ変更の追跡
    - セキュリティイベントの記録
    """
    __tablename__ = "audit_logs"

    # 基本情報
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # 操作情報
    action = Column(String(100), nullable=False, index=True, comment="操作種別")
    entity_type = Column(String(100), nullable=True, comment="対象エンティティ種別")
    entity_id = Column(Integer, nullable=True, comment="対象エンティティID")

    # 詳細情報
    details = Column(JSON, nullable=True, comment="操作詳細情報")
    ip_address = Column(String(45), nullable=True, comment="操作元IPアドレス")
    user_agent = Column(Text, nullable=True, comment="ユーザーエージェント")

    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # リレーション
    user = relationship("User")

    # インデックス
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_created', 'created_at'),
    )


# =========================================
# エクスポート
# =========================================

# 全モデルをエクスポート（Alembicの自動インポート用）
__all__ = [
    "Base",
    "User",
    "KanteiRecord",
    "EmailHistory",
    "TemplateSettings",
    "SystemSettings",
    "AuditLog"
]