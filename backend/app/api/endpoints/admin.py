"""
管理者専用のFastAPIエンドポイント

管理者権限が必要な操作:
- ユーザー管理（一覧・詳細・権限変更）
- システム設定管理
- 監査ログ閲覧
- 統計情報取得
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, desc
from typing import List, Optional
from datetime import datetime, timezone

from ...database import get_db
from ...models import User, KanteiRecord, EmailHistory, AuditLog
from ...schemas.auth import UserResponse, UserStatusUpdateRequest
from ...api.dependencies.auth import verify_admin_user
from pydantic import BaseModel, Field

router = APIRouter()


# =================================
# レスポンススキーマ（管理者用）
# =================================

class UserListResponse(BaseModel):
    """ユーザー一覧レスポンス"""
    id: int
    email: str
    business_name: Optional[str]
    operator_name: Optional[str]
    is_active: bool
    is_superuser: bool
    subscription_status: str
    created_at: datetime
    kantei_count: int = 0


class SystemStatsResponse(BaseModel):
    """システム統計レスポンス"""
    total_users: int
    active_users: int
    admin_users: int
    total_kantei_records: int
    total_emails_sent: int




# =================================
# ユーザー管理エンドポイント
# =================================

@router.get("/users", response_model=List[UserListResponse])
async def list_users(
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する件数"),
    search: Optional[str] = Query(None, description="検索キーワード（メール・屋号）"),
    admin_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """ユーザー一覧取得（管理者専用）

    Args:
        skip: スキップする件数
        limit: 取得する件数
        search: 検索キーワード
        admin_user: 管理者ユーザー
        db: データベースセッション

    Returns:
        List[UserListResponse]: ユーザー一覧
    """
    # ベースクエリ
    query = select(
        User.id,
        User.email,
        User.business_name,
        User.operator_name,
        User.is_active,
        User.is_superuser,
        User.subscription_status,
        User.created_at,
        func.count(KanteiRecord.id).label('kantei_count')
    ).select_from(
        User.__table__.outerjoin(KanteiRecord.__table__)
    ).where(
        User.deleted_at.is_(None)
    ).group_by(User.id)

    # 検索条件追加
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            and_(
                User.email.ilike(search_filter) |
                User.business_name.ilike(search_filter) |
                User.operator_name.ilike(search_filter)
            )
        )

    # ソート・ページング
    query = query.order_by(desc(User.created_at)).offset(skip).limit(limit)

    result = db.execute(query)
    users = result.fetchall()

    return [
        UserListResponse(
            id=user.id,
            email=user.email,
            business_name=user.business_name,
            operator_name=user.operator_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            subscription_status=user.subscription_status,
            created_at=user.created_at,
            kantei_count=user.kantei_count
        )
        for user in users
    ]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_detail(
    user_id: int,
    admin_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """ユーザー詳細取得（管理者専用）

    Args:
        user_id: ユーザーID
        admin_user: 管理者ユーザー
        db: データベースセッション

    Returns:
        UserResponse: ユーザー詳細情報

    Raises:
        HTTPException: ユーザーが見つからない場合
    """
    stmt = select(User).where(
        User.id == user_id,
        User.deleted_at.is_(None)
    )
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
        )

    return UserResponse.model_validate(user)


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    update_data: UserStatusUpdateRequest,
    admin_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """ユーザーステータス更新（管理者専用）

    Args:
        user_id: ユーザーID
        update_data: ステータス更新データ
        admin_user: 管理者ユーザー
        db: データベースセッション

    Returns:
        dict: 更新結果

    Raises:
        HTTPException: ユーザーが見つからない場合
    """
    stmt = select(User).where(
        User.id == user_id,
        User.deleted_at.is_(None)
    )
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
        )

    # 更新処理（subscription_statusは管理機能から除外）
    update_fields = []
    if update_data.is_active is not None:
        user.is_active = update_data.is_active
        update_fields.append("is_active")

    if update_data.is_superuser is not None:
        user.is_superuser = update_data.is_superuser
        update_fields.append("is_superuser")

    if update_fields:
        user.updated_at = datetime.now(timezone.utc)
        db.commit()

        # 監査ログ記録
        audit_log = AuditLog(
            user_id=admin_user.id,
            action="update_user",
            entity_type="User",
            entity_id=user.id,
            details={
                "updated_fields": update_fields,
                "updated_by": admin_user.email,
                "reason": update_data.reason
            }
        )
        db.add(audit_log)
        db.commit()

    return {
        "success": True,
        "message": f"ユーザー {user.email} の情報を更新しました",
        "updated_fields": update_fields
    }


# =================================
# システム統計エンドポイント
# =================================

@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    admin_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """システム統計情報取得（管理者専用）

    Args:
        admin_user: 管理者ユーザー
        db: データベースセッション

    Returns:
        SystemStatsResponse: システム統計情報
    """
    # ユーザー統計
    total_users = db.execute(
        select(func.count(User.id)).where(User.deleted_at.is_(None))
    ).scalar()

    active_users = db.execute(
        select(func.count(User.id)).where(
            and_(User.is_active == True, User.deleted_at.is_(None))
        )
    ).scalar()

    admin_users = db.execute(
        select(func.count(User.id)).where(
            and_(User.is_superuser == True, User.deleted_at.is_(None))
        )
    ).scalar()

    # 鑑定記録統計
    total_kantei_records = db.execute(
        select(func.count(KanteiRecord.id)).where(KanteiRecord.deleted_at.is_(None))
    ).scalar()

    # メール送信統計
    total_emails_sent = db.execute(
        select(func.count(EmailHistory.id)).where(EmailHistory.status == "sent")
    ).scalar()

    return SystemStatsResponse(
        total_users=total_users or 0,
        active_users=active_users or 0,
        admin_users=admin_users or 0,
        total_kantei_records=total_kantei_records or 0,
        total_emails_sent=total_emails_sent or 0
    )


# =================================
# ユーザー一括操作エンドポイント
# =================================

@router.delete("/users/bulk-delete")
async def bulk_delete_users(
    admin_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """全ユーザーデータの一括削除（管理者専用）

    警告: この操作は取り消せません

    Args:
        admin_user: 管理者ユーザー
        db: データベースセッション

    Returns:
        dict: 削除結果
    """
    # 現在の管理者以外の全ユーザーを削除
    users_to_delete = db.execute(
        select(User).where(
            and_(
                User.id != admin_user.id,  # 実行中の管理者は削除しない
                User.deleted_at.is_(None)
            )
        )
    ).scalars().all()

    deleted_count = len(users_to_delete)
    deleted_emails = [user.email for user in users_to_delete]

    # 論理削除実行
    for user in users_to_delete:
        user.deleted_at = datetime.now(timezone.utc)
        user.is_active = False

    # 監査ログ記録
    audit_log = AuditLog(
        user_id=admin_user.id,
        action="bulk_delete_users",
        entity_type="User",
        entity_id=None,
        details={
            "deleted_count": deleted_count,
            "deleted_emails": deleted_emails,
            "executed_by": admin_user.email
        }
    )
    db.add(audit_log)
    db.commit()

    return {
        "success": True,
        "message": f"{deleted_count}件のユーザーデータを削除しました",
        "deleted_count": deleted_count,
        "preserved_admin": admin_user.email
    }


@router.delete("/users/bulk-purge")
async def bulk_purge_users(
    admin_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """論理削除済みユーザーの物理削除（管理者専用）

    警告: この操作は取り消せません

    Args:
        admin_user: 管理者ユーザー
        db: データベースセッション

    Returns:
        dict: 削除結果
    """
    # 論理削除済みユーザーを物理削除
    users_to_purge = db.execute(
        select(User).where(
            and_(
                User.id != admin_user.id,  # 実行中の管理者は削除しない
                User.deleted_at.is_not(None)
            )
        )
    ).scalars().all()

    purged_count = len(users_to_purge)
    purged_emails = [user.email for user in users_to_purge]

    # 物理削除実行
    for user in users_to_purge:
        db.delete(user)

    # 監査ログ記録
    audit_log = AuditLog(
        user_id=admin_user.id,
        action="bulk_purge_users",
        entity_type="User",
        entity_id=None,
        details={
            "purged_count": purged_count,
            "purged_emails": purged_emails,
            "executed_by": admin_user.email
        }
    )
    db.add(audit_log)
    db.commit()

    return {
        "success": True,
        "message": f"{purged_count}件の論理削除済みユーザーデータを物理削除しました",
        "purged_count": purged_count,
        "preserved_admin": admin_user.email
    }


# =================================
# 権限テスト用エンドポイント
# =================================

@router.get("/test-admin")
async def test_admin_access(admin_user: User = Depends(verify_admin_user)):
    """管理者権限テスト用エンドポイント

    Args:
        admin_user: 管理者ユーザー

    Returns:
        dict: 管理者情報
    """
    return {
        "message": "管理者権限でアクセス成功",
        "admin_user": {
            "id": admin_user.id,
            "email": admin_user.email,
            "is_superuser": admin_user.is_superuser
        }
    }