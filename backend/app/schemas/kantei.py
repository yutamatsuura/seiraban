"""
鑑定関連のPydanticスキーマ定義 - Phase A-2a
九星気学・姓名判断・吉方位の統合鑑定システム

技術仕様: Pydantic v2 + FastAPI + SQLAlchemy連携
エンドポイント対象:
- POST /api/kantei/calculate - 九星気学・姓名判断の計算処理
- GET /api/kantei/templates - 81パターンテキストテンプレート取得
"""

from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum


# =========================================
# 基本型定義・列挙型
# =========================================

class GenderType(str, Enum):
    """性別の定義"""
    MALE = "male"
    FEMALE = "female"


class KanteiStatusType(str, Enum):
    """鑑定状態の定義"""
    CREATED = "created"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# =========================================
# リクエストスキーマ（入力用）
# =========================================

class ClientInfoRequest(BaseModel):
    """クライアント基本情報入力スキーマ

    P-002 鑑定書作成ページのフォーム入力に対応

    必須項目:
    - name: 氏名（姓名判断計算に使用）
    - birth_date: 生年月日（九星気学計算に使用）
    - gender: 性別（計算ロジックに影響）
    - email: クライアントメールアドレス（PDF送信用）

    任意項目:
    - birth_time: 出生時刻（詳細計算用）
    - birth_place: 出生地（将来的な吉方位計算強化用）
    """
    name: str = Field(..., min_length=1, max_length=100, description="クライアント氏名")
    birth_date: date = Field(..., description="生年月日")
    birth_time: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="出生時刻（HH:MM形式）")
    gender: GenderType = Field(..., description="性別")
    birth_place: Optional[str] = Field(None, max_length=100, description="出生地")
    email: EmailStr = Field(..., description="クライアントメールアドレス")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "山田太郎",
                "birth_date": "1990-03-15",
                "birth_time": "10:30",
                "gender": "male",
                "birth_place": "東京都",
                "email": "yamada@example.com"
            }
        }
    )


class KanteiCalculateRequest(BaseModel):
    """鑑定計算実行リクエストスキーマ"""
    client_info: ClientInfoRequest = Field(..., description="クライアント基本情報")
    custom_message: Optional[str] = Field(None, max_length=500, description="カスタムメッセージ（任意）")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "client_info": {
                    "name": "山田太郎",
                    "birth_date": "1990-03-15",
                    "gender": "male",
                    "email": "yamada@example.com"
                },
                "custom_message": "特別なご要望がございましたら記載ください"
            }
        }
    )


# =========================================
# レスポンススキーマ（出力用）
# =========================================

class KyuseiKigakuResult(BaseModel):
    """九星気学計算結果スキーマ"""
    honmei: str = Field(..., description="本命星")
    gekkyu: str = Field(..., description="月命星")
    nichikyu: str = Field(..., description="日命星")
    seikaku: str = Field(..., description="性格特徴の説明文")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "honmei": "七赤金星",
                "gekkyu": "三碧木星",
                "nichikyu": "九紫火星",
                "seikaku": "社交性に優れ、華やかな魅力を持つ人です。コミュニケーション能力が高く、多くの人から愛される傾向があります。"
            }
        }
    )


class SeimeiHandanResult(BaseModel):
    """姓名判断計算結果スキーマ"""
    soukaku: int = Field(..., ge=1, le=200, description="総格")
    tenkaku: int = Field(..., ge=1, le=100, description="天格")
    jinkaku: int = Field(..., ge=1, le=100, description="人格")
    chikaku: int = Field(..., ge=1, le=100, description="地格")
    gaikaku: int = Field(..., ge=1, le=100, description="外格")
    hyoka: str = Field(..., description="総合評価")
    tenti_kantei: Optional[List[Dict[str, Any]]] = Field(default=None, description="天地による鑑定")
    data: Optional[Dict[str, Any]] = Field(default=None, description="詳細データ（技術者向け）")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "soukaku": 32,
                "tenkaku": 18,
                "jinkaku": 24,
                "chikaku": 14,
                "gaikaku": 8,
                "hyoka": "大吉 - 非常に良い運勢を持つ名前です。リーダーシップを発揮し、成功を収める可能性が高いでしょう。",
                "tenti_kantei": [
                    {
                        "対象": "争花",
                        "評価": "天地同数(偶数)",
                        "詳細": "相手に平気または何気なく、気に障ることを言って怒らせます、しかし、本人は何故起こっているのか気が付きません。人間関係で揉めたり、喧嘩、大騒動を起こしやすいです。また、健康を害しやすいです。",
                        "タイプ": "天地同数"
                    },
                    {
                        "対象": "争 花",
                        "評価": "天地総同数",
                        "詳細": "激しい喧嘩、トラブル、事故、事件が起きやすくなります。人生に苦労が多いです。",
                        "タイプ": "天地総同数"
                    }
                ]
            }
        }
    )


class KichikouiResult(BaseModel):
    """吉方位計算結果スキーマ"""
    honnen: str = Field(..., description="本年の吉方位")
    gekkan: str = Field(..., description="今月の吉方位")
    suishin: str = Field(..., description="推奨事項・アドバイス")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "honnen": "東",
                "gekkan": "南東",
                "suishin": "旅行や引越しに最適な時期です。特に東方向への移動が幸運を呼び込むでしょう。"
            }
        }
    )


class KanteiCalculationResponse(BaseModel):
    """鑑定計算結果統合レスポンススキーマ

    九星気学・姓名判断・吉方位の全結果を含む
    P-002 プレビューセクションでの表示用
    """
    id: int = Field(..., description="鑑定記録ID")
    client_name: str = Field(..., description="クライアント氏名")
    kyusei_kigaku: KyuseiKigakuResult = Field(..., description="九星気学結果")
    seimei_handan: SeimeiHandanResult = Field(..., description="姓名判断結果")
    kichihoui: KichikouiResult = Field(..., description="吉方位結果")
    template_ids: List[int] = Field(..., description="使用する81パターンテンプレートIDリスト")
    status: KanteiStatusType = Field(..., description="計算状態")
    created_at: datetime = Field(..., description="作成日時")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "client_name": "山田太郎",
                "kyusei_kigaku": {
                    "honmei": "七赤金星",
                    "gekkyu": "三碧木星",
                    "nichikyu": "九紫火星",
                    "seikaku": "社交性に優れ、華やかな魅力を持つ人です。"
                },
                "seimei_handan": {
                    "soukaku": 32,
                    "tenkaku": 18,
                    "jinkaku": 24,
                    "chikaku": 14,
                    "gaikaku": 8,
                    "hyoka": "大吉 - 非常に良い運勢を持つ名前です。"
                },
                "kichihoui": {
                    "honnen": "東",
                    "gekkan": "南東",
                    "suishin": "旅行や引越しに最適な時期です。"
                },
                "template_ids": [15, 23, 41, 67],
                "status": "completed",
                "created_at": "2024-01-15T10:30:00"
            }
        }
    )


class KanteiTemplate(BaseModel):
    """81パターンテキストテンプレートスキーマ"""
    id: int = Field(..., description="テンプレートID")
    category: str = Field(..., description="カテゴリ（九星気学/姓名判断/吉方位など）")
    pattern_name: str = Field(..., description="パターン名")
    title: str = Field(..., description="タイトル")
    content: str = Field(..., description="テンプレート本文")
    keywords: List[str] = Field(..., description="関連キーワード")
    usage_count: int = Field(0, description="使用回数")
    is_active: bool = Field(True, description="有効フラグ")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 15,
                "category": "九星気学",
                "pattern_name": "七赤金星_基本性格",
                "title": "華やかな魅力の持ち主",
                "content": "あなたは七赤金星の生まれで、自然な魅力と社交性を持っています。周囲の人々を惹きつける力があり、コミュニケーション能力に長けています。",
                "keywords": ["社交性", "魅力", "コミュニケーション"],
                "usage_count": 156,
                "is_active": True
            }
        }
    )


class KanteiTemplatesResponse(BaseModel):
    """テンプレート一覧取得レスポンススキーマ"""
    total: int = Field(..., description="総テンプレート数")
    templates: List[KanteiTemplate] = Field(..., description="テンプレートリスト")
    categories: List[str] = Field(..., description="利用可能カテゴリ一覧")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 81,
                "templates": [
                    {
                        "id": 15,
                        "category": "九星気学",
                        "pattern_name": "七赤金星_基本性格",
                        "title": "華やかな魅力の持ち主",
                        "content": "テンプレート本文...",
                        "keywords": ["社交性", "魅力"],
                        "usage_count": 156,
                        "is_active": True
                    }
                ],
                "categories": ["九星気学", "姓名判断", "吉方位", "総合運勢"]
            }
        }
    )


# =========================================
# エラーレスポンススキーマ
# =========================================

class KanteiErrorResponse(BaseModel):
    """鑑定エラーレスポンススキーマ"""
    error_code: str = Field(..., description="エラーコード")
    error_message: str = Field(..., description="エラーメッセージ")
    details: Optional[Dict[str, Any]] = Field(None, description="エラー詳細情報")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error_code": "CALCULATION_FAILED",
                "error_message": "九星気学の計算に失敗しました",
                "details": {
                    "field": "birth_date",
                    "reason": "日付が不正です"
                }
            }
        }
    )


# =========================================
# メッセージレスポンス（共通）
# =========================================

class MessageResponse(BaseModel):
    """汎用メッセージレスポンススキーマ"""
    success: bool = Field(..., description="処理成功フラグ")
    message: str = Field(..., description="メッセージ")
    data: Optional[Dict[str, Any]] = Field(None, description="追加データ")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "処理が正常に完了しました",
                "data": {"processed_count": 1}
            }
        }
    )


# =========================================
# エクスポート
# =========================================

__all__ = [
    # 列挙型
    "GenderType",
    "KanteiStatusType",

    # リクエストスキーマ
    "ClientInfoRequest",
    "KanteiCalculateRequest",

    # レスポンススキーマ
    "KyuseiKigakuResult",
    "SeimeiHandanResult",
    "KichikouiResult",
    "KanteiCalculationResponse",
    "KanteiTemplate",
    "KanteiTemplatesResponse",

    # エラー・メッセージスキーマ
    "KanteiErrorResponse",
    "MessageResponse"
]