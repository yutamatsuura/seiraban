"""
CHAIN-002: 認証フロー - エンドポイント連鎖テスト

ユーザーストーリー: 鑑定士がログインして各機能にアクセス
エンドポイント連鎖: 1.1→1.2

フロー:
1. POST /api/auth/login - ログイン認証（JWT取得）
2. GET /api/auth/verify - トークン検証と権限確認

実装要件:
- NEON PostgreSQL実データ使用
- JWT認証フロー確認
- 権限チェック動作確認
"""

import pytest
import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

# フィクスチャはconftest.pyから自動的に読み込まれる
from ..schemas.auth import LoginRequest, LoginResponse, UserResponse
from ..models import User


class TestChain002AuthFlow:
    """CHAIN-002: 認証フロー連鎖テスト"""

    def test_chain_002_complete_auth_flow(self, db_session: Session, test_user: User, test_user_data: dict):
        """
        CHAIN-002メインテスト: ログイン→トークン検証の完全フロー

        フロー:
        1.1 POST /api/auth/login - ログイン認証（JWT取得）
        1.2 GET /api/auth/verify - トークン検証と権限確認
        """
        print(f"\n=== CHAIN-002: 認証フロー開始 ===")
        print(f"テストユーザー: {test_user.email}")
        print(f"サブスクリプション状態: {test_user.subscription_status}")

        # === 1.1 POST /api/auth/login - ログイン認証 ===
        print(f"\n--- Step 1.1: POST /api/auth/login ---")

        # 実際のAPIを呼び出し
        with httpx.Client(base_url="http://localhost:8500") as client:
            login_response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": test_user_data["email"],
                    "password": test_user_data["password"]
                }
            )

        # レスポンス検証
        assert login_response.status_code == 200, f"ログイン失敗: {login_response.text}"

        login_data = login_response.json()
        print(f"ログイン成功: {login_data}")

        # LoginResponseスキーマ検証
        assert "access_token" in login_data
        assert "token_type" in login_data
        assert "user_id" in login_data
        assert "subscription_status" in login_data

        assert login_data["token_type"] == "bearer"
        assert login_data["user_id"] == test_user.id
        assert login_data["subscription_status"] == test_user.subscription_status

        access_token = login_data["access_token"]
        assert len(access_token) > 20  # JWT形式確認

        print(f"JWT取得成功: {access_token[:30]}...")

        # === 1.2 GET /api/auth/verify - トークン検証 ===
        print(f"\n--- Step 1.2: GET /api/auth/verify ---")

        # Authorization ヘッダーでトークン送信
        with httpx.Client(base_url="http://localhost:8500") as client:
            verify_response = client.get(
                "/api/v1/auth/verify",
                headers={"Authorization": f"Bearer {access_token}"}
            )

        # レスポンス検証
        assert verify_response.status_code == 200, f"トークン検証失敗: {verify_response.text}"

        verify_data = verify_response.json()
        print(f"トークン検証成功: {verify_data}")

        # UserResponseスキーマ検証
        assert "id" in verify_data
        assert "email" in verify_data
        assert "business_name" in verify_data
        assert "operator_name" in verify_data
        assert "subscription_status" in verify_data
        assert "is_active" in verify_data

        # データ整合性確認
        assert verify_data["id"] == test_user.id
        assert verify_data["email"] == test_user.email
        assert verify_data["business_name"] == test_user.business_name
        assert verify_data["operator_name"] == test_user.operator_name
        assert verify_data["subscription_status"] == test_user.subscription_status
        assert verify_data["is_active"] == test_user.is_active

        print(f"=== CHAIN-002: 認証フロー完了 ===")
        print(f"結果: ログイン→トークン検証の連鎖成功")

    def test_chain_002_step_1_1_login_success(self, db_session: Session, test_user: User, test_user_data: dict):
        """
        Step 1.1単体テスト: POST /api/auth/login - 正常ログイン
        """
        print(f"\n=== Step 1.1単体テスト: ログイン認証 ===")

        with httpx.Client(base_url="http://localhost:8500") as client:
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": test_user_data["email"],
                    "password": test_user_data["password"]
                }
            )

        assert response.status_code == 200
        data = response.json()

        # JWT形式確認
        token_parts = data["access_token"].split(".")
        assert len(token_parts) == 3  # header.payload.signature

        # UTAGE連携確認（モック実装）
        if test_user.utage_user_id:
            assert "utage_user_id" in data
            assert data["utage_user_id"] == str(test_user.utage_user_id)

        print(f"ログイン認証成功: ユーザーID {data['user_id']}")

    def test_chain_002_step_1_1_login_invalid_credentials(self, db_session: Session, test_user: User):
        """
        Step 1.1エラーテスト: POST /api/auth/login - 無効な認証情報
        """
        print(f"\n=== Step 1.1エラーテスト: 無効な認証情報 ===")

        with httpx.Client(base_url="http://localhost:8500") as client:
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": test_user.email,
                    "password": "wrong_password"
                }
            )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "正しくありません" in data["detail"]

        print(f"無効認証情報のエラーハンドリング成功")

    def test_chain_002_step_1_2_verify_success(self, db_session: Session, test_user: User, test_user_data: dict):
        """
        Step 1.2単体テスト: GET /api/auth/verify - 正常トークン検証
        """
        print(f"\n=== Step 1.2単体テスト: トークン検証 ===")

        # まずログインしてトークン取得
        with httpx.Client(base_url="http://localhost:8500") as client:
            login_response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": test_user_data["email"],
                    "password": test_user_data["password"]
                }
            )

            assert login_response.status_code == 200
            access_token = login_response.json()["access_token"]

            # トークン検証
            verify_response = client.get(
                "/api/v1/auth/verify",
                headers={"Authorization": f"Bearer {access_token}"}
            )

        assert verify_response.status_code == 200
        data = verify_response.json()

        # 権限チェック確認
        assert data["is_active"] == True
        assert data["subscription_status"] in ["active", "inactive", "suspended"]

        # 個人情報保護確認（パスワードハッシュは含まれない）
        assert "hashed_password" not in data
        assert "password" not in data

        print(f"トークン検証成功: ユーザー {data['email']}")

    def test_chain_002_step_1_2_verify_invalid_token(self, db_session: Session):
        """
        Step 1.2エラーテスト: GET /api/auth/verify - 無効なトークン
        """
        print(f"\n=== Step 1.2エラーテスト: 無効なトークン ===")

        with httpx.Client(base_url="http://localhost:8500") as client:
            response = client.get(
                "/api/v1/auth/verify",
                headers={"Authorization": "Bearer invalid_token_here"}
            )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

        print(f"無効トークンのエラーハンドリング成功")

    def test_chain_002_step_1_2_verify_missing_token(self, db_session: Session):
        """
        Step 1.2エラーテスト: GET /api/auth/verify - トークンなし
        """
        print(f"\n=== Step 1.2エラーテスト: Authorizationヘッダーなし ===")

        with httpx.Client(base_url="http://localhost:8500") as client:
            response = client.get("/api/v1/auth/verify")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

        print(f"トークンなしのエラーハンドリング成功")

    def test_chain_002_subscription_status_verification(self, db_session: Session, test_user: User, test_user_data: dict):
        """
        CHAIN-002付加テスト: サブスクリプション状態の確認
        """
        print(f"\n=== CHAIN-002付加テスト: サブスクリプション状態確認 ===")

        # ログイン→検証のフロー実行
        with httpx.Client(base_url="http://localhost:8500") as client:
            # ログイン
            login_response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": test_user_data["email"],
                    "password": test_user_data["password"]
                }
            )

            login_data = login_response.json()
            access_token = login_data["access_token"]

            # 検証
            verify_response = client.get(
                "/api/v1/auth/verify",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            verify_data = verify_response.json()

        # 両ステップでサブスクリプション状態が一致することを確認
        assert login_data["subscription_status"] == verify_data["subscription_status"]
        assert login_data["user_id"] == verify_data["id"]

        print(f"サブスクリプション状態の整合性確認成功: {verify_data['subscription_status']}")

    def test_chain_002_database_connection_verification(self, db_session: Session):
        """
        CHAIN-002基盤テスト: NEON PostgreSQL接続確認
        """
        print(f"\n=== CHAIN-002基盤テスト: データベース接続確認 ===")

        # データベース接続確認
        result = db_session.execute(text("SELECT 1 as test_connection"))
        connection_test = result.scalar()

        assert connection_test == 1

        # ユーザーテーブル存在確認
        result = db_session.execute(
            text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'users'")
        )
        users_table_exists = result.scalar()

        assert users_table_exists > 0

        print(f"NEON PostgreSQL接続確認成功")

    def test_chain_002_end_to_end_timing(self, db_session: Session, test_user: User, test_user_data: dict):
        """
        CHAIN-002性能テスト: エンドツーエンドの応答時間確認
        """
        print(f"\n=== CHAIN-002性能テスト: 応答時間確認 ===")

        start_time = datetime.now()

        with httpx.Client(base_url="http://localhost:8500") as client:
            # ログイン
            login_start = datetime.now()
            login_response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": test_user_data["email"],
                    "password": test_user_data["password"]
                }
            )
            login_end = datetime.now()

            access_token = login_response.json()["access_token"]

            # 検証
            verify_start = datetime.now()
            verify_response = client.get(
                "/api/v1/auth/verify",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            verify_end = datetime.now()

        end_time = datetime.now()

        # 応答時間計算
        login_time = (login_end - login_start).total_seconds()
        verify_time = (verify_end - verify_start).total_seconds()
        total_time = (end_time - start_time).total_seconds()

        assert login_response.status_code == 200
        assert verify_response.status_code == 200

        print(f"ログイン応答時間: {login_time:.3f}秒")
        print(f"検証応答時間: {verify_time:.3f}秒")
        print(f"総処理時間: {total_time:.3f}秒")

        # 基本的な性能要件確認（開発環境）
        assert login_time < 5.0  # 5秒以内
        assert verify_time < 2.0  # 2秒以内
        assert total_time < 10.0  # 10秒以内

        print(f"CHAIN-002性能要件クリア")