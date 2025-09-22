"""
PDF生成サービス層テスト - 実データ接続テスト
Phase S-2b担当: 実データでの動作保証

技術要件:
- NEON PostgreSQL実接続
- ReportLab PDF生成テスト
- TemplateSettings連携テスト
- 実データ必須（モック禁止）
"""

import pytest
import tempfile
import os
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime

# テスト用の環境変数読み込み
from dotenv import load_dotenv
load_dotenv("/Users/lennon/projects/inoue4/sindankantei/.env.local")

from ..database import get_db, SessionLocal
from ..models import User, KanteiRecord, TemplateSettings
from ..services.pdf_service import get_pdf_service, PDFServiceError
from ..schemas.pdf import PDFGenerationRequest


class TestPDFService:
    """PDF生成サービステスト - 実データ使用"""

    @pytest.fixture(scope="function")
    def db_session(self):
        """実データベース接続セッション"""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @pytest.fixture(scope="function")
    def test_user(self, db_session: Session):
        """テスト用ユーザー作成"""
        # 既存ユーザーを検索または作成
        user = db_session.query(User).filter(User.email == "test@sindankantei.com").first()

        if not user:
            user = User(
                email="test@sindankantei.com",
                hashed_password="$2b$12$hashed_password_example",
                business_name="テスト鑑定事務所",
                operator_name="テスト運営者",
                is_active=True,
                subscription_status="active"
            )
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)

        return user

    @pytest.fixture(scope="function")
    def test_template_settings(self, db_session: Session, test_user: User):
        """テスト用テンプレート設定作成"""
        # 既存設定を検索または作成
        template = db_session.query(TemplateSettings).filter(
            TemplateSettings.user_id == test_user.id
        ).first()

        if not template:
            template = TemplateSettings(
                user_id=test_user.id,
                business_name="テスト鑑定事務所",
                operator_name="テスト運営者",
                color_theme="blue",
                font_family="default",
                layout_style="standard"
            )
            db_session.add(template)
            db_session.commit()
            db_session.refresh(template)

        return template

    @pytest.fixture(scope="function")
    def test_kantei_record(self, db_session: Session, test_user: User):
        """テスト用鑑定記録作成"""
        # 実際の鑑定データ構造
        client_info = {
            "name": "田中花子",
            "birth_date": "1990-05-15",
            "birth_time": "10:30",
            "gender": "女性",
            "birth_place": "東京都"
        }

        calculation_result = {
            "kyusei_kigaku": {
                "honmei_star": "九紫火星",
                "gekkei_star": "八白土星",
                "nichimei_star": "七赤金星",
                "fortune_summary": "創造性豊かで情熱的な性格。リーダーシップを発揮できる年です。"
            },
            "seimei_handan": {
                "tenkaku": 12,
                "jinkaku": 15,
                "chikaku": 8,
                "soukaku": 20,
                "overall_rating": "大吉",
                "summary": "バランスの取れた画数構成で運勢良好です。"
            },
            "kichihoui": {
                "this_month": "東",
                "this_year": "南東",
                "recommendations": "新しいことを始めるのに適した時期です。東や南東方面への移動が吉。"
            }
        }

        record = KanteiRecord(
            user_id=test_user.id,
            client_name="田中花子",
            client_email="tanaka@example.com",
            client_info=client_info,
            calculation_result=calculation_result,
            status="created",
            custom_message="特別な開運アドバイスをお送りします。"
        )

        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)

        return record

    def test_database_connection(self, db_session: Session):
        """データベース接続テスト"""
        # 実際のNEON PostgreSQL接続確認
        result = db_session.execute("SELECT 1 as test")
        assert result.fetchone()[0] == 1
        print("✅ NEON PostgreSQL接続成功")

    def test_pdf_service_initialization(self):
        """PDF生成サービス初期化テスト"""
        pdf_service = get_pdf_service()
        assert pdf_service is not None
        assert pdf_service.storage_path.exists()
        print("✅ PDF生成サービス初期化成功")

    def test_reportlab_basic_functionality(self):
        """ReportLab基本機能テスト"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            # 基本的なPDF生成テスト
            c = canvas.Canvas(tmp_file.name, pagesize=A4)
            c.drawString(100, 750, "ReportLab Test PDF")
            c.save()

            # ファイルが作成されたか確認
            assert Path(tmp_file.name).exists()
            assert Path(tmp_file.name).stat().st_size > 0

            # クリーンアップ
            os.unlink(tmp_file.name)

        print("✅ ReportLab基本機能動作確認")

    def test_pdf_generation_with_real_data(
        self,
        db_session: Session,
        test_user: User,
        test_kantei_record: KanteiRecord,
        test_template_settings: TemplateSettings
    ):
        """実データを使用したPDF生成テスト"""
        pdf_service = get_pdf_service()

        request = PDFGenerationRequest(
            kantei_record_id=test_kantei_record.id,
            custom_message="これは実データテストです。",
            use_template_settings=True
        )

        # 実際のPDF生成実行
        try:
            response = pdf_service.generate_pdf(
                db=db_session,
                request=request,
                user_id=test_user.id
            )

            # レスポンス検証
            assert response.success is True
            assert response.pdf_id == test_kantei_record.id
            assert response.pdf_url is not None
            assert response.file_size > 0
            assert response.page_count > 0
            assert response.generated_at is not None

            # データベース更新確認
            db_session.refresh(test_kantei_record)
            assert test_kantei_record.pdf_url is not None
            assert test_kantei_record.pdf_file_size > 0
            assert test_kantei_record.pdf_generated_at is not None
            assert test_kantei_record.status == "completed"

            # 実際のPDFファイル存在確認
            pdf_path = Path(response.pdf_url)
            assert pdf_path.exists()
            assert pdf_path.stat().st_size > 0

            print(f"✅ PDF生成成功: {response.pdf_url}")
            print(f"   ファイルサイズ: {response.file_size} bytes")
            print(f"   ページ数: {response.page_count}")

        except Exception as e:
            pytest.fail(f"PDF生成エラー: {str(e)}")

    def test_pdf_download_info_generation(
        self,
        db_session: Session,
        test_user: User,
        test_kantei_record: KanteiRecord
    ):
        """PDFダウンロード情報生成テスト"""
        # 先にPDFを生成
        pdf_service = get_pdf_service()

        generation_request = PDFGenerationRequest(
            kantei_record_id=test_kantei_record.id,
            use_template_settings=False
        )

        pdf_service.generate_pdf(
            db=db_session,
            request=generation_request,
            user_id=test_user.id
        )

        # ダウンロード情報取得テスト
        try:
            download_response = pdf_service.get_pdf_download_info(
                db=db_session,
                kantei_record_id=test_kantei_record.id,
                user_id=test_user.id
            )

            # レスポンス検証
            assert download_response.success is True
            assert download_response.file_name is not None
            assert "田中花子" in download_response.file_name or "tanaka" in download_response.file_name.lower()
            assert download_response.file_size > 0
            assert download_response.content_type == "application/pdf"
            assert download_response.download_url is not None
            assert download_response.expires_at is not None

            print(f"✅ ダウンロード情報生成成功: {download_response.file_name}")
            print(f"   有効期限: {download_response.expires_at}")

        except Exception as e:
            pytest.fail(f"ダウンロード情報生成エラー: {str(e)}")

    def test_pdf_status_check(
        self,
        db_session: Session,
        test_user: User,
        test_kantei_record: KanteiRecord
    ):
        """PDFステータス確認テスト"""
        pdf_service = get_pdf_service()

        # PDF生成前のステータス確認
        status_before = pdf_service.get_pdf_status(
            db=db_session,
            kantei_record_id=test_kantei_record.id,
            user_id=test_user.id
        )

        assert status_before["pdf_status"] == "pending"
        print("✅ PDF生成前ステータス確認: pending")

        # PDF生成実行
        generation_request = PDFGenerationRequest(
            kantei_record_id=test_kantei_record.id,
            use_template_settings=False
        )

        pdf_service.generate_pdf(
            db=db_session,
            request=generation_request,
            user_id=test_user.id
        )

        # PDF生成後のステータス確認
        status_after = pdf_service.get_pdf_status(
            db=db_session,
            kantei_record_id=test_kantei_record.id,
            user_id=test_user.id
        )

        assert status_after["pdf_status"] == "completed"
        assert status_after["pdf_url"] is not None
        print("✅ PDF生成後ステータス確認: completed")

    def test_template_settings_integration(
        self,
        db_session: Session,
        test_user: User,
        test_kantei_record: KanteiRecord,
        test_template_settings: TemplateSettings
    ):
        """TemplateSettings連携テスト"""
        pdf_service = get_pdf_service()

        # テンプレート設定を使用してPDF生成
        request = PDFGenerationRequest(
            kantei_record_id=test_kantei_record.id,
            use_template_settings=True
        )

        try:
            response = pdf_service.generate_pdf(
                db=db_session,
                request=request,
                user_id=test_user.id
            )

            assert response.success is True

            # 生成されたPDFファイルの内容確認（簡易）
            pdf_path = Path(response.pdf_url)
            assert pdf_path.exists()

            # PDFファイルサイズが妥当範囲内かチェック
            file_size = pdf_path.stat().st_size
            assert 1000 < file_size < 10_000_000  # 1KB - 10MB

            print(f"✅ TemplateSettings連携PDF生成成功")
            print(f"   テンプレート設定: {test_template_settings.business_name}")
            print(f"   ファイルサイズ: {file_size} bytes")

        except Exception as e:
            pytest.fail(f"TemplateSettings連携エラー: {str(e)}")

    def test_error_handling(
        self,
        db_session: Session,
        test_user: User
    ):
        """エラーハンドリングテスト"""
        pdf_service = get_pdf_service()

        # 存在しない鑑定記録IDでのテスト
        invalid_request = PDFGenerationRequest(
            kantei_record_id=99999,  # 存在しないID
            use_template_settings=False
        )

        with pytest.raises(PDFServiceError) as exc_info:
            pdf_service.generate_pdf(
                db=db_session,
                request=invalid_request,
                user_id=test_user.id
            )

        assert "見つかりません" in str(exc_info.value)
        print("✅ エラーハンドリング動作確認")

    @pytest.fixture(scope="class", autouse=True)
    def cleanup_test_data(self):
        """テスト終了後のクリーンアップ"""
        yield

        # テスト用PDFファイルのクリーンアップ
        pdf_service = get_pdf_service()
        if pdf_service.storage_path.exists():
            for pdf_file in pdf_service.storage_path.glob("kantei_*.pdf"):
                try:
                    pdf_file.unlink()
                except Exception:
                    pass  # クリーンアップエラーは無視

        print("✅ テストクリーンアップ完了")


if __name__ == "__main__":
    # 直接実行時の単発テスト
    import asyncio

    def run_direct_test():
        """直接実行テスト"""
        db = SessionLocal()

        try:
            # データベース接続確認
            result = db.execute("SELECT 1 as test")
            print(f"✅ データベース接続成功: {result.fetchone()[0]}")

            # PDF生成サービス初期化確認
            pdf_service = get_pdf_service()
            print(f"✅ PDF生成サービス初期化成功: {pdf_service.storage_path}")

            print("🎉 基本動作確認完了")

        except Exception as e:
            print(f"❌ エラー: {str(e)}")
        finally:
            db.close()

    run_direct_test()