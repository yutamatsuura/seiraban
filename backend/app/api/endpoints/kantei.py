"""
鑑定関連APIエンドポイント - Phase A-2a
九星気学・姓名判断・吉方位の統合鑑定システム

技術スタック: FastAPI + SQLAlchemy 2.0 + Pydantic v2
エンドポイント:
- POST /api/kantei/calculate - 九星気学・姓名判断の計算処理
- GET /api/kantei/templates - 81パターンテキストテンプレート取得

注意: この段階では仮実装のみ（サービス層実装は後続Phase）
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ...database import get_db
from ...schemas.kantei import (
    KanteiCalculateRequest,
    KanteiCalculationResponse,
    KanteiTemplate,
    KanteiTemplatesResponse,
    KanteiErrorResponse,
    MessageResponse,
    KyuseiKigakuResult,
    SeimeiHandanResult,
    KichikouiResult,
    GenderType,
    KanteiStatusType
)
from ...models import KanteiRecord, User
from ...services.template_service import TemplateService
from ...services.kantei_service import KanteiService

router = APIRouter()

# =========================================
# エンドポイント 2.1: 鑑定計算実行
# =========================================

@router.post(
    "/calculate",
    response_model=KanteiCalculationResponse,
    responses={
        400: {"model": KanteiErrorResponse, "description": "入力データエラー"},
        500: {"model": KanteiErrorResponse, "description": "計算処理エラー"}
    },
    summary="九星気学・姓名判断の統合計算",
    description="""
    クライアント基本情報から九星気学・姓名判断・吉方位を計算し、鑑定結果を返す。

    **処理フロー:**
    1. クライアント情報のバリデーション
    2. 九星気学計算（本命星・月命星・日命星）
    3. 姓名判断計算（総格・天格・人格・地格・外格）
    4. 吉方位計算（年間・月間）
    5. 81パターンテンプレートの該当判定
    6. 結果の統合・保存

    **計算精度:**
    - 九星気学: 旧暦対応の高精度計算
    - 姓名判断: 漢字画数による正統派計算
    - 吉方位: 個人の九星に基づく方位算出

    **外部依存:**
    - systemフォルダの既存計算ロジック
    - 81パターンテキストデータベース
    """
)
async def calculate_kantei(
    request: KanteiCalculateRequest,
    db: Session = Depends(get_db)
) -> KanteiCalculationResponse:
    """九星気学・姓名判断の統合計算実行"""
    try:
        # TODO: 認証機能実装後にuser_idを取得
        user_id = 1  # 仮のuser_id

        # サービス層で計算実行
        service = KanteiService(db)
        response = await service.calculate_kantei(request, user_id)

        return response

    except HTTPException:
        raise
    except Exception as e:
        # 予期しないエラーのハンドリング
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "CALCULATION_FAILED",
                "error_message": "鑑定計算中にエラーが発生しました",
                "details": {"original_error": str(e)}
            }
        )


# =========================================
# エンドポイント 2.2: 81パターンテンプレート取得
# =========================================

@router.get(
    "/templates",
    response_model=KanteiTemplatesResponse,
    responses={
        404: {"model": KanteiErrorResponse, "description": "テンプレートが見つかりません"}
    },
    summary="81パターンテキストテンプレート取得",
    description="""
    鑑定書に使用する81パターンのテキストテンプレートを取得する。

    **テンプレート構成:**
    - 九星気学パターン: 9種類 × 9パターン = 81種類
    - 姓名判断パターン: 画数組み合わせによる分類
    - 吉方位パターン: 方位別アドバイス

    **フィルタリング機能:**
    - カテゴリ別取得（九星気学/姓名判断/吉方位）
    - アクティブフラグによる有効テンプレートのみ取得
    - 使用頻度による人気順ソート

    **キャッシュ対応:**
    - テンプレートデータは頻繁に変更されないため、Redis等でキャッシュ推奨
    """
)
def get_kantei_templates(
    category: Optional[str] = Query(None, description="カテゴリフィルタ（九星気学/姓名判断/吉方位）"),
    active_only: bool = Query(True, description="有効なテンプレートのみ取得"),
    limit: int = Query(100, ge=1, le=200, description="取得件数制限"),
    db: Session = Depends(get_db)
) -> KanteiTemplatesResponse:
    """81パターンテキストテンプレート取得"""
    try:
        service = TemplateService(db)
        return service.get_kantei_templates(
            category=category,
            active_only=active_only,
            limit=limit
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "TEMPLATE_FETCH_FAILED",
                "error_message": "テンプレート取得中にエラーが発生しました",
                "details": {"original_error": str(e)}
            }
        )


# =========================================
# 補助エンドポイント: ヘルスチェック
# =========================================

@router.get(
    "/health",
    response_model=MessageResponse,
    summary="鑑定システムヘルスチェック",
    description="鑑定システムの稼働状況と依存サービスの状態を確認する"
)
async def health_check(
    db: Session = Depends(get_db)
) -> MessageResponse:
    """鑑定システムヘルスチェック"""
    try:
        # TODO: 実装時に各種サービスの稼働確認を追加
        # - データベース接続確認
        # - 計算ロジックサービス確認
        # - テンプレートデータベース確認

        return MessageResponse(
            success=True,
            message="鑑定システムは正常に稼働しています",
            data={
                "database": "connected",
                "calculation_service": "ready",
                "template_service": "ready",
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        return MessageResponse(
            success=False,
            message="鑑定システムで問題が検出されました",
            data={
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


# =========================================
# エクスポート用ルーター設定
# =========================================

# ルーター設定情報は api.py で設定

# エラーハンドラ等の追加設定（必要に応じて）