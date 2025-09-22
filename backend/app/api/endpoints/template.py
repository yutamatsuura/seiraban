"""
テンプレート設定関連のFastAPIエンドポイント

エンドポイント:
- GET /api/template/settings - テンプレート設定取得
- PUT /api/template/update - テンプレート設定更新
- POST /api/template/upload-logo - ロゴ画像アップロード

テンプレート設定の管理とファイルアップロード機能を提供
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import os
import uuid
import shutil

from ...database import get_db
from ...schemas.template import (
    TemplateSettingsResponse,
    TemplateSettingsUpdate,
    LogoUploadResponse,
    MessageResponse,
    TemplateSettingsRequest
)
from ...models import TemplateSettings, User
from ...services.template_service import TemplateService

router = APIRouter()

# ファイルアップロード設定
UPLOAD_DIR = "uploads/logos"
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# アップロードディレクトリの作成
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/settings", response_model=TemplateSettingsResponse)
def get_template_settings(
    db: Session = Depends(get_db)
):
    """テンプレート設定取得エンドポイント

    現在のユーザーのテンプレート設定を取得します。
    設定が存在しない場合はデフォルト設定で新規作成します。
    """
    # TODO: 認証実装後に実際のuser_idを取得
    user_id = 1  # 仮のuser_id

    service = TemplateService(db)
    return service.get_template_settings(user_id)


@router.put("/update", response_model=TemplateSettingsResponse)
def update_template_settings(
    settings: TemplateSettingsUpdate,
    db: Session = Depends(get_db)
):
    """テンプレート設定更新エンドポイント

    指定されたフィールドのみを更新します（部分更新対応）。
    """
    # TODO: 認証実装後に実際のuser_idを取得
    user_id = 1  # 仮のuser_id

    service = TemplateService(db)
    result = service.update_template_settings(user_id, settings)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="テンプレート設定が見つかりません。先に設定を取得してください。"
        )

    return result


@router.post("/upload-logo", response_model=LogoUploadResponse)
async def upload_logo(
    logo_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """ロゴ画像アップロードエンドポイント

    ロゴ画像をアップロードし、テンプレート設定に保存します。
    対応形式: JPG, PNG（最大2MB）
    """
    # TODO: 認証実装後に実際のuser_idを取得
    user_id = 1  # 仮のuser_id

    # ファイル検証
    if not logo_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ファイルが選択されていません。"
        )

    # ファイル内容読み込み
    file_content = await logo_file.read()

    try:
        service = TemplateService(db)
        return service.upload_logo(user_id, file_content, logo_file.filename)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/logo", response_model=MessageResponse)
def delete_logo(
    db: Session = Depends(get_db)
):
    """ロゴ画像削除エンドポイント（追加機能）

    現在設定されているロゴ画像を削除します。
    """
    # TODO: 認証実装後に実際のuser_idを取得
    user_id = 1  # 仮のuser_id

    service = TemplateService(db)
    success = service.delete_logo(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="削除するロゴ画像が見つかりません。"
        )

    return MessageResponse(
        success=True,
        message="ロゴ画像が正常に削除されました。"
    )