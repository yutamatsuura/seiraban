"""
認証関連のFastAPIエンドポイント

Phase A-1a: 認証API群
- 1.1 POST /api/auth/login - ログイン認証
- 1.2 GET /api/auth/verify - トークン検証と権限確認
- 1.3 POST /api/auth/register - ユーザー登録
- 1.4 POST /api/auth/logout - ログアウト処理
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from ...database import get_db
from ...schemas.auth import (
    LoginRequest,
    LoginResponse,
    UserResponse,
    MessageResponse,
    AuthErrorResponse,
    RegistrationRequest,
    RegistrationResponse
)
from ...services.auth_service import AuthService
from ...api.dependencies.auth import get_current_user
from ...models import User
from ...core.security import authenticate_user

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """ログイン認証

    Args:
        credentials: ログイン情報（メール・パスワード）
        db: データベースセッション

    Returns:
        LoginResponse: JWT トークンとユーザー情報

    Raises:
        HTTPException: 認証失敗時
    """
    auth_service = AuthService(db)
    return auth_service.authenticate_and_login(credentials)


@router.get("/verify", response_model=UserResponse)
async def verify_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """トークン検証と権限確認

    Args:
        current_user: 認証されたユーザー（依存関数から取得）
        db: データベースセッション

    Returns:
        UserResponse: ユーザー詳細情報

    Note:
        - Authorization ヘッダーで "Bearer <token>" 形式で送信
        - トークンが無効な場合は 401 エラー
    """
    auth_service = AuthService(db)
    return auth_service.verify_user_token(current_user)


@router.post("/register", response_model=RegistrationResponse)
async def register(
    registration_data: RegistrationRequest,
    db: Session = Depends(get_db)
):
    """ユーザー登録

    Args:
        registration_data: 登録情報
        db: データベースセッション

    Returns:
        RegistrationResponse: 登録結果

    Raises:
        HTTPException: 登録失敗時（409: メールアドレス重複等）

    Note:
        - パスワードは自動的にハッシュ化される
        - 作成時のsubscription_statusは"active"に設定
    """
    auth_service = AuthService(db)
    return auth_service.register_user(registration_data)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ログアウト処理

    Args:
        current_user: 認証されたユーザー
        db: データベースセッション

    Returns:
        MessageResponse: ログアウト完了メッセージ

    Note:
        - JWT はステートレスなため、サーバー側では特別な処理なし
        - クライアント側でトークンを削除する必要がある
        - 将来的にはトークンブラックリスト機能を追加予定
    """
    auth_service = AuthService(db)
    logout_result = auth_service.logout_user(current_user)

    return MessageResponse(
        success=logout_result["success"],
        message=logout_result["message"]
    )


# エラーハンドリング用のエンドポイント（開発・テスト用）
@router.get("/test-error", response_model=AuthErrorResponse)
async def test_error_response():
    """エラーレスポンステスト用エンドポイント（開発用）

    Returns:
        AuthErrorResponse: サンプルエラーレスポンス
    """
    return AuthErrorResponse(
        error_code="TEST_ERROR",
        message="これはテスト用のエラーレスポンスです",
        detail="開発環境でのエラーハンドリング確認用"
    )


# 開発環境用の管理者昇格エンドポイント
@router.post("/promote-to-admin", response_model=MessageResponse)
async def promote_to_admin(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """ユーザーを管理者に昇格（開発用）

    Args:
        credentials: ログイン情報
        db: データベースセッション

    Returns:
        MessageResponse: 昇格結果

    Note:
        開発環境でのテスト用エンドポイント
        本番環境では削除または制限する必要がある
    """
    auth_service = AuthService(db)

    # ユーザー認証
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません"
        )

    # 管理者権限付与
    user.is_superuser = True
    user.updated_at = datetime.now(timezone.utc)
    db.commit()

    return MessageResponse(
        success=True,
        message=f"{user.email} を管理者に昇格しました"
    )