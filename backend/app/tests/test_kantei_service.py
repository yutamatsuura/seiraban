"""
鑑定サービスのテスト - Phase S-2a
実データを使用した統合テスト（モック禁止）

技術要件:
- NEON PostgreSQL実接続
- SQLAlchemy 2.0 + Alembic
- 実データでの動作検証
"""

import pytest
import asyncio
from datetime import date, datetime
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.database import get_db, engine
from app.main import app
from app.models import User, KanteiRecord
from app.services.kantei_service import KanteiService, KanteiCalculationService
from app.schemas.kantei import (
    KanteiCalculateRequest,
    ClientInfoRequest,
    GenderType,
    KanteiStatusType
)


class TestKanteiService:
    """鑑定サービス統合テスト

    実際のNEON PostgreSQLデータベースを使用し、
    モックを使わない本格的な動作検証を実行
    """

    @pytest.fixture
    def db_session(self):
        """テスト用DBセッション取得"""
        session = next(get_db())
        yield session
        session.close()

    @pytest.fixture
    def test_client(self):
        """FastAPIテストクライアント"""
        return TestClient(app)

    @pytest.fixture
    def test_user(self, db_session: Session):
        """テスト用ユーザー作成"""
        import uuid

        # 既存ユーザーをクリーンアップ
        existing_user = db_session.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            db_session.delete(existing_user)
            db_session.commit()

        # ユニークなメールアドレスでユーザー作成
        unique_email = f"test+{uuid.uuid4().hex[:8]}@example.com"
        user = User(
            email=unique_email,
            hashed_password="hashed_password_here",
            business_name="テスト占いサロン",
            operator_name="テスト 花子",
            is_active=True,
            subscription_status="active"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        yield user

        # テスト後のクリーンアップ
        db_session.query(KanteiRecord).filter(KanteiRecord.user_id == user.id).delete()
        db_session.delete(user)
        db_session.commit()

    @pytest.fixture
    def sample_client_info(self):
        """テスト用クライアント情報"""
        return ClientInfoRequest(
            name="山田太郎",
            birth_date=date(1990, 3, 15),
            birth_time="10:30",
            gender=GenderType.MALE,
            birth_place="東京都",
            email="yamada@example.com"
        )

    @pytest.fixture
    def sample_kantei_request(self, sample_client_info):
        """テスト用鑑定リクエスト"""
        return KanteiCalculateRequest(
            client_info=sample_client_info,
            custom_message="特別なご要望がございます"
        )

    # =========================================
    # 基本計算機能テスト
    # =========================================

    @pytest.mark.asyncio
    async def test_kantei_calculation_basic(
        self,
        db_session: Session,
        test_user: User,
        sample_kantei_request: KanteiCalculateRequest
    ):
        """基本鑑定計算テスト

        九星気学・姓名判断・吉方位の統合計算が正常に動作することを確認
        """
        # サービス初期化
        service = KanteiService(db_session)

        # 鑑定計算実行
        result = await service.calculate_kantei(sample_kantei_request, test_user.id)

        # レスポンス基本検証
        assert result.id > 0
        assert result.client_name == "山田太郎"
        assert result.status == KanteiStatusType.COMPLETED
        assert result.created_at is not None

        # 九星気学結果検証
        kyusei = result.kyusei_kigaku
        assert kyusei.honmei in ["一白水星", "二黒土星", "三碧木星", "四緑木星", "五黄土星",
                               "六白金星", "七赤金星", "八白土星", "九紫火星"]
        assert kyusei.gekkyu in ["一白水星", "二黒土星", "三碧木星", "四緑木星", "五黄土星",
                               "六白金星", "七赤金星", "八白土星", "九紫火星"]
        assert kyusei.nichikyu in ["一白水星", "二黒土星", "三碧木星", "四緑木星", "五黄土星",
                                 "六白金星", "七赤金星", "八白土星", "九紫火星"]
        assert len(kyusei.seikaku) > 20  # 性格説明文の長さ検証

        # 姓名判断結果検証
        seimei = result.seimei_handan
        assert 1 <= seimei.soukaku <= 200
        assert 1 <= seimei.tenkaku <= 100
        assert 1 <= seimei.jinkaku <= 100
        assert 1 <= seimei.chikaku <= 100
        assert 1 <= seimei.gaikaku <= 100
        assert len(seimei.hyoka) > 10  # 評価文の長さ検証

        # 吉方位結果検証
        kichihoui = result.kichihoui
        assert kichihoui.honnen in ["北", "北東", "東", "南東", "南", "南西", "西", "北西"]
        assert kichihoui.gekkan in ["北", "北東", "東", "南東", "南", "南西", "西", "北西"]
        assert len(kichihoui.suishin) > 20  # アドバイス文の長さ検証

        # テンプレートID検証
        assert len(result.template_ids) >= 3
        assert all(isinstance(tid, int) for tid in result.template_ids)

    @pytest.mark.asyncio
    async def test_kantei_calculation_various_names(
        self,
        db_session: Session,
        test_user: User
    ):
        """様々な名前での鑑定計算テスト

        漢字、ひらがな、カタカナなど様々な文字種の名前で計算が正常に動作することを確認
        """
        test_cases = [
            {"name": "佐藤花子", "gender": GenderType.FEMALE},
            {"name": "田中 一郎", "gender": GenderType.MALE},  # スペース入り
            {"name": "鈴木さくら", "gender": GenderType.FEMALE},  # ひらがなあり
            {"name": "高橋ユウキ", "gender": GenderType.MALE},  # カタカナあり
            {"name": "中村", "gender": GenderType.MALE},  # 一文字名
        ]

        service = KanteiService(db_session)

        for case in test_cases:
            # テストケース毎にリクエスト作成
            client_info = ClientInfoRequest(
                name=case["name"],
                birth_date=date(1985, 6, 20),
                gender=case["gender"],
                email="test@example.com"
            )
            request = KanteiCalculateRequest(client_info=client_info)

            # 計算実行
            result = await service.calculate_kantei(request, test_user.id)

            # 基本検証
            assert result.client_name == case["name"]
            assert result.status == KanteiStatusType.COMPLETED

            # 姓名判断の格計算が合理的な値であることを確認
            seimei = result.seimei_handan
            assert seimei.soukaku > 0
            assert seimei.tenkaku > 0
            assert seimei.jinkaku > 0

    # =========================================
    # データベース保存テスト
    # =========================================

    @pytest.mark.asyncio
    async def test_kantei_record_persistence(
        self,
        db_session: Session,
        test_user: User,
        sample_kantei_request: KanteiCalculateRequest
    ):
        """鑑定記録のデータベース保存テスト

        計算結果が正しくデータベースに保存されることを確認
        """
        service = KanteiService(db_session)

        # 計算実行
        result = await service.calculate_kantei(sample_kantei_request, test_user.id)

        # データベースから記録を取得
        saved_record = db_session.query(KanteiRecord).filter(
            KanteiRecord.id == result.id
        ).first()

        assert saved_record is not None
        assert saved_record.user_id == test_user.id
        assert saved_record.client_name == "山田太郎"
        assert saved_record.client_email == "yamada@example.com"
        assert saved_record.status == "completed"
        assert saved_record.custom_message == "特別なご要望がございます"

        # JSON保存データの検証
        client_info = saved_record.client_info
        assert client_info["name"] == "山田太郎"
        assert client_info["birth_date"] == "1990-03-15"
        assert client_info["gender"] == "male"

        calculation_result = saved_record.calculation_result
        assert "kyusei_kigaku" in calculation_result
        assert "seimei_handan" in calculation_result
        assert "kichihoui" in calculation_result
        assert "template_ids" in calculation_result

    @pytest.mark.asyncio
    async def test_multiple_kantei_records(
        self,
        db_session: Session,
        test_user: User
    ):
        """複数鑑定記録の処理テスト

        同一ユーザーによる複数の鑑定が正しく処理されることを確認
        """
        service = KanteiService(db_session)

        # 3つの異なる鑑定を実行
        test_clients = [
            {"name": "田中一郎", "birth_date": date(1980, 5, 10)},
            {"name": "佐藤花子", "birth_date": date(1992, 8, 25)},
            {"name": "鈴木太郎", "birth_date": date(1975, 12, 3)},
        ]

        results = []
        for client in test_clients:
            client_info = ClientInfoRequest(
                name=client["name"],
                birth_date=client["birth_date"],
                gender=GenderType.MALE,
                email="test@example.com"
            )
            request = KanteiCalculateRequest(client_info=client_info)
            result = await service.calculate_kantei(request, test_user.id)
            results.append(result)

        # 全て異なる記録として保存されていることを確認
        assert len(set(r.id for r in results)) == 3
        assert len(set(r.client_name for r in results)) == 3

        # 履歴取得テスト
        history = service.get_user_kantei_history(test_user.id, limit=10)
        assert len(history) >= 3

        # 作成日時順（降順）でソートされていることを確認
        for i in range(len(history) - 1):
            assert history[i].created_at >= history[i + 1].created_at

    # =========================================
    # エラーハンドリングテスト
    # =========================================

    @pytest.mark.asyncio
    async def test_invalid_input_handling(
        self,
        db_session: Session,
        test_user: User
    ):
        """不正入力のエラーハンドリングテスト"""
        service = KanteiService(db_session)

        # 空の名前
        with pytest.raises(Exception):  # 実際のエラー型に応じて調整
            client_info = ClientInfoRequest(
                name="",
                birth_date=date(1990, 3, 15),
                gender=GenderType.MALE,
                email="test@example.com"
            )
            request = KanteiCalculateRequest(client_info=client_info)
            await service.calculate_kantei(request, test_user.id)

    # =========================================
    # パフォーマンステスト
    # =========================================

    @pytest.mark.asyncio
    async def test_calculation_performance(
        self,
        db_session: Session,
        test_user: User
    ):
        """計算パフォーマンステスト

        計算処理が合理的な時間内で完了することを確認
        """
        service = KanteiService(db_session)

        client_info = ClientInfoRequest(
            name="パフォーマンステスト",
            birth_date=date(1988, 7, 14),
            gender=GenderType.FEMALE,
            email="perf@example.com"
        )
        request = KanteiCalculateRequest(client_info=client_info)

        # 実行時間測定
        start_time = datetime.now()
        result = await service.calculate_kantei(request, test_user.id)
        end_time = datetime.now()

        execution_time = (end_time - start_time).total_seconds()

        # 10秒以内で完了することを確認
        assert execution_time < 10.0
        assert result.status == KanteiStatusType.COMPLETED

    # =========================================
    # APIエンドポイント統合テスト
    # =========================================

    def test_kantei_calculate_endpoint_integration(
        self,
        test_client: TestClient,
        db_session: Session,
        test_user: User
    ):
        """鑑定計算APIエンドポイント統合テスト

        HTTPリクエスト経由での動作確認
        """
        # リクエストデータ
        request_data = {
            "client_info": {
                "name": "API テスト太郎",
                "birth_date": "1987-04-22",
                "gender": "male",
                "email": "apitest@example.com"
            },
            "custom_message": "APIテストメッセージ"
        }

        # APIエンドポイント呼び出し
        response = test_client.post("/api/v1/kantei/calculate", json=request_data)

        # HTTPステータス確認
        assert response.status_code == 200

        # レスポンス内容確認
        data = response.json()
        assert data["client_name"] == "API テスト太郎"
        assert data["status"] == "completed"
        assert "kyusei_kigaku" in data
        assert "seimei_handan" in data
        assert "kichihoui" in data
        assert "template_ids" in data

    def test_kantei_templates_endpoint_integration(
        self,
        test_client: TestClient
    ):
        """81パターンテンプレート取得APIエンドポイント統合テスト"""
        # APIエンドポイント呼び出し
        response = test_client.get("/api/v1/kantei/templates")

        # HTTPステータス確認
        assert response.status_code == 200

        # レスポンス内容確認
        data = response.json()
        assert "total" in data
        assert "templates" in data
        assert "categories" in data
        assert data["total"] > 0
        assert len(data["templates"]) > 0
        assert len(data["categories"]) > 0

        # テンプレート構造確認
        template = data["templates"][0]
        assert "id" in template
        assert "category" in template
        assert "pattern_name" in template
        assert "title" in template
        assert "content" in template
        assert "keywords" in template

    def test_kantei_health_endpoint(
        self,
        test_client: TestClient
    ):
        """鑑定システムヘルスチェックエンドポイントテスト"""
        response = test_client.get("/api/v1/kantei/health")

        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "data" in data

    # =========================================
    # クリーンアップ・ユーティリティメソッド
    # =========================================

    def cleanup_test_data(self, db_session: Session, test_user: User):
        """テストデータクリーンアップ

        テスト実行後の不要データ削除
        """
        # テストユーザーの鑑定記録を削除
        db_session.query(KanteiRecord).filter(
            KanteiRecord.user_id == test_user.id
        ).delete()

        # テストユーザーを削除
        db_session.delete(test_user)
        db_session.commit()


# =========================================
# テスト設定・フィクスチャ
# =========================================

@pytest.fixture(scope="session")
def event_loop():
    """pytest-asyncio用のイベントループ設定"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# テスト実行例コマンド（プロジェクトルートから）:
# python -m pytest backend/app/tests/test_kantei_service.py -v
# python -m pytest backend/app/tests/test_kantei_service.py::TestKanteiService::test_kantei_calculation_basic -v