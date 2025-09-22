"""
履歴管理API群 - FastAPIエンドポイント実装

Phase A-3a: 履歴管理API群
- 4.1 `/api/kantei/history` GET - 鑑定履歴一覧取得
- 4.2 `/api/kantei/detail/{id}` GET - 鑑定詳細情報取得
- 4.3 `/api/kantei/resend/{id}` POST - 鑑定書再送信

技術仕様:
- SQLAlchemyモデル: KanteiRecord, EmailHistory（作成済み）
- ページネーション機能
- P-004モックアップ準拠
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ...database import get_db
from ...schemas.history import (
    KanteiHistoryResponse,
    KanteiHistoryItem,
    KanteiDetailResponse,
    ResendRequest,
    ResendResponse,
    MessageResponse,
    validate_pagination_params,
    calculate_offset,
    calculate_total_pages
)
from ...models import KanteiRecord, EmailHistory
from ...services.history_service import HistoryService

router = APIRouter()


# =========================================
# 4.1 鑑定履歴一覧取得 GET /api/kantei/history
# =========================================

@router.get("/history", response_model=KanteiHistoryResponse)
async def get_kantei_history(
    page: int = Query(1, ge=1, description="ページ番号"),
    limit: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
    search: Optional[str] = Query(None, description="検索クエリ（クライアント名）"),
    status: Optional[str] = Query(None, description="ステータスフィルター"),
    db: Session = Depends(get_db)
):
    """
    鑑定履歴一覧取得

    ページネーション機能付きで鑑定履歴を取得します。
    各履歴にはメール送信回数と最終送信日時も含まれます。

    Args:
        page: ページ番号（1以上）
        limit: 1ページあたりの件数（1-100）
        db: データベースセッション

    Returns:
        KanteiHistoryResponse: ページネーション情報と履歴一覧

    Raises:
        HTTPException: データベースエラー時
    """
    try:
        # TODO: 認証実装後にuser_idを取得
        user_id = 1  # 仮のユーザーID

        # サービス層を使用して履歴取得
        history_service = HistoryService(db)

        return history_service.get_kantei_history(
            user_id=user_id,
            page=page,
            limit=limit,
            search_query=search,
            status_filter=status
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"鑑定履歴の取得に失敗しました: {str(e)}"
        )


# =========================================
# 4.2 鑑定詳細情報取得 GET /api/kantei/detail/{id}
# =========================================

@router.get("/detail/{id}", response_model=KanteiDetailResponse)
async def get_kantei_detail(
    id: int,
    db: Session = Depends(get_db)
):
    """
    鑑定詳細情報取得

    指定されたIDの鑑定記録の詳細情報を取得します。
    メール送信履歴も含まれます。

    Args:
        id: 鑑定記録ID
        db: データベースセッション

    Returns:
        KanteiDetailResponse: 鑑定詳細情報

    Raises:
        HTTPException: 鑑定記録が見つからない場合、またはデータベースエラー時
    """
    try:
        # TODO: 認証実装後にuser_idを取得
        user_id = 1  # 仮のユーザーID

        # サービス層を使用して詳細取得
        history_service = HistoryService(db)

        return history_service.get_kantei_detail(
            kantei_id=id,
            user_id=user_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"鑑定詳細情報の取得に失敗しました: {str(e)}"
        )


# =========================================
# 4.3 鑑定書再送信 POST /api/kantei/resend/{id}
# =========================================

@router.post("/resend/{id}", response_model=ResendResponse)
async def resend_kantei(
    id: int,
    resend_data: ResendRequest,
    db: Session = Depends(get_db)
):
    """
    鑑定書再送信

    指定された鑑定記録のPDFを再送信します。
    新しいメール履歴レコードが作成されます。

    Args:
        id: 鑑定記録ID
        resend_data: 再送信情報（メールアドレス、送信者名、メッセージ）
        db: データベースセッション

    Returns:
        ResendResponse: 送信結果情報

    Raises:
        HTTPException: 鑑定記録が見つからない場合、またはメール送信エラー時
    """
    try:
        # TODO: 認証実装後にuser_idを取得
        user_id = 1  # 仮のユーザーID

        # サービス層を使用して再送信
        history_service = HistoryService(db)

        return history_service.resend_kantei(
            kantei_id=id,
            user_id=user_id,
            resend_data=resend_data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"鑑定書の再送信に失敗しました: {str(e)}"
        )


# =========================================
# 補助エンドポイント
# =========================================

@router.get("/health", response_model=MessageResponse)
async def health_check():
    """
    履歴管理API群のヘルスチェック

    Returns:
        MessageResponse: API稼働状況
    """
    return MessageResponse(
        message="履歴管理API群は正常に稼働しています",
        success=True
    )