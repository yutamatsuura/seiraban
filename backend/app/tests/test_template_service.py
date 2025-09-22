"""
テンプレートサービス層テスト - Phase S-1b
実データテスト (モック禁止)

対象機能:
- テンプレート設定のCRUD操作
- ファイルアップロード・画像処理・ストレージ管理
- 81パターンテンプレートの管理
"""

import pytest
import os
import tempfile
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..services.template_service import TemplateService
from ..models import TemplateSettings, User
from ..schemas.template import (
    TemplateSettingsUpdate,
    TemplateSettingsCreate
)
from ..core.security import get_password_hash


class TestTemplateService:
    """テンプレートサービス層テスト (実データ主義)"""

    @pytest.fixture(scope="function")
    def template_service(self, db_session: Session) -> TemplateService:
        """テンプレートサービスインスタンス作成"""
        return TemplateService(db_session)

    @pytest.fixture(scope="function")
    def test_user(self, db_session: Session) -> User:
        """テスト用ユーザー作成（実データ）"""
        timestamp = datetime.now().timestamp()
        user = User(
            email=f"template.test.{timestamp}@example.com",
            hashed_password=get_password_hash("test_password"),
            business_name="テストサロン",
            operator_name="テスト太郎",
            subscription_status="active",
            is_active=True
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        yield user

        # テスト後のクリーンアップ
        db_session.delete(user)
        db_session.commit()

    @pytest.fixture(scope="function")
    def sample_logo_file(self) -> bytes:
        """サンプルロゴファイル（PNG形式）のバイナリデータ"""
        # 実際の小さなPNG画像のバイナリデータ（1x1 pixel transparent PNG）
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc```\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        return png_data

    # =========================================
    # テンプレート設定CRUD操作テスト
    # =========================================

    def test_get_template_settings_new_user(
        self,
        template_service: TemplateService,
        test_user: User
    ):
        """新規ユーザーのテンプレート設定取得（デフォルト設定作成）"""
        result = template_service.get_template_settings(test_user.id)

        # デフォルト設定で作成されることを確認
        assert result is not None
        assert result.user_id == test_user.id
        assert result.business_name == "占いサロン 星花"
        assert result.operator_name == "星野 花子"
        assert result.color_theme == "default"
        assert result.font_family == "default"
        assert result.layout_style == "standard"
        assert result.settings_version == "1.0"
        assert result.logo_url is None

    def test_get_template_settings_existing_user(
        self,
        template_service: TemplateService,
        test_user: User,
        db_session: Session
    ):
        """既存設定ありユーザーのテンプレート設定取得"""
        # 事前にテンプレート設定を作成
        existing_settings = TemplateSettings(
            user_id=test_user.id,
            business_name="カスタムサロン",
            operator_name="カスタム太郎",
            color_theme="blue",
            font_family="custom",
            layout_style="modern",
            settings_version="2.0"
        )
        db_session.add(existing_settings)
        db_session.commit()

        result = template_service.get_template_settings(test_user.id)

        # 既存設定が取得されることを確認
        assert result is not None
        assert result.user_id == test_user.id
        assert result.business_name == "カスタムサロン"
        assert result.operator_name == "カスタム太郎"
        assert result.color_theme == "blue"
        assert result.font_family == "custom"
        assert result.layout_style == "modern"

    def test_update_template_settings_success(
        self,
        template_service: TemplateService,
        test_user: User
    ):
        """テンプレート設定更新成功"""
        # まず設定を作成
        template_service.get_template_settings(test_user.id)

        # 更新データ
        update_data = TemplateSettingsUpdate(
            business_name="更新後サロン",
            operator_name="更新太郎",
            color_theme="green"
        )

        result = template_service.update_template_settings(test_user.id, update_data)

        # 更新されたデータを確認
        assert result is not None
        assert result.business_name == "更新後サロン"
        assert result.operator_name == "更新太郎"
        assert result.color_theme == "green"
        # 更新されていないフィールドはそのまま
        assert result.font_family == "default"
        assert result.layout_style == "standard"

    def test_update_template_settings_not_found(
        self,
        template_service: TemplateService,
        test_user: User
    ):
        """存在しないユーザーの設定更新（失敗）"""
        update_data = TemplateSettingsUpdate(business_name="存在しないユーザー")

        # 存在しないユーザーIDで更新試行
        result = template_service.update_template_settings(99999, update_data)

        # Noneが返されることを確認
        assert result is None

    def test_create_template_settings(
        self,
        template_service: TemplateService,
        test_user: User
    ):
        """テンプレート設定新規作成"""
        create_data = TemplateSettingsCreate(
            business_name="新規サロン",
            operator_name="新規太郎",
            color_theme="purple",
            font_family="gothic",
            layout_style="compact"
        )

        result = template_service.create_template_settings(test_user.id, create_data)

        # 作成されたデータを確認
        assert result is not None
        assert result.user_id == test_user.id
        assert result.business_name == "新規サロン"
        assert result.operator_name == "新規太郎"
        assert result.color_theme == "purple"
        assert result.font_family == "gothic"
        assert result.layout_style == "compact"

    # =========================================
    # ファイルアップロード・画像処理テスト
    # =========================================

    def test_upload_logo_success(
        self,
        template_service: TemplateService,
        test_user: User,
        sample_logo_file: bytes
    ):
        """ロゴアップロード成功"""
        result = template_service.upload_logo(
            test_user.id,
            sample_logo_file,
            "test_logo.png"
        )

        # アップロード結果を確認
        assert result.success is True
        assert result.file_size == len(sample_logo_file)
        assert "/uploads/logos/" in result.logo_url
        assert result.logo_url.endswith(".png")
        assert "正常にアップロードされました" in result.message

        # ファイルが実際に保存されているか確認
        file_path = result.logo_url.replace("/uploads/logos/", "")
        full_path = os.path.join(template_service.UPLOAD_DIR, file_path)
        assert os.path.exists(full_path)

        # データベースにも保存されているか確認
        settings = template_service.get_template_settings(test_user.id)
        assert settings.logo_url == result.logo_url
        assert settings.logo_file_size == len(sample_logo_file)

    def test_upload_logo_invalid_extension(
        self,
        template_service: TemplateService,
        test_user: User
    ):
        """無効な拡張子でアップロード失敗"""
        invalid_file = b"fake_content"

        with pytest.raises(ValueError, match="JPEGまたはPNG形式の画像ファイルのみ"):
            template_service.upload_logo(
                test_user.id,
                invalid_file,
                "test_file.txt"
            )

    def test_upload_logo_file_too_large(
        self,
        template_service: TemplateService,
        test_user: User
    ):
        """ファイルサイズ上限超過でアップロード失敗"""
        # 3MBのダミーファイル（上限2MBを超過）
        large_file = b"x" * (3 * 1024 * 1024)

        with pytest.raises(ValueError, match="ファイルサイズは2MB以下"):
            template_service.upload_logo(
                test_user.id,
                large_file,
                "large_file.png"
            )

    def test_upload_logo_no_filename(
        self,
        template_service: TemplateService,
        test_user: User,
        sample_logo_file: bytes
    ):
        """ファイル名なしでアップロード失敗"""
        with pytest.raises(ValueError, match="ファイルが選択されていません"):
            template_service.upload_logo(
                test_user.id,
                sample_logo_file,
                ""
            )

    def test_delete_logo_success(
        self,
        template_service: TemplateService,
        test_user: User,
        sample_logo_file: bytes
    ):
        """ロゴ削除成功"""
        # まずロゴをアップロード
        upload_result = template_service.upload_logo(
            test_user.id,
            sample_logo_file,
            "test_logo.png"
        )

        # ロゴを削除
        delete_result = template_service.delete_logo(test_user.id)

        # 削除結果を確認
        assert delete_result is True

        # ファイルが削除されているか確認
        file_path = upload_result.logo_url.replace("/uploads/logos/", "")
        full_path = os.path.join(template_service.UPLOAD_DIR, file_path)
        assert not os.path.exists(full_path)

        # データベースからも削除されているか確認
        settings = template_service.get_template_settings(test_user.id)
        assert settings.logo_url is None
        assert settings.logo_file_size is None

    def test_delete_logo_not_found(
        self,
        template_service: TemplateService,
        test_user: User
    ):
        """ロゴ削除失敗（ロゴが存在しない）"""
        result = template_service.delete_logo(test_user.id)

        # 削除失敗を確認
        assert result is False

    # =========================================
    # 81パターンテンプレート管理テスト
    # =========================================

    def test_get_kantei_templates_all(
        self,
        template_service: TemplateService
    ):
        """全テンプレート取得"""
        result = template_service.get_kantei_templates()

        # レスポンス構造を確認
        assert result.total == 81
        assert len(result.templates) > 0
        assert "九星気学" in result.categories
        assert "姓名判断" in result.categories
        assert "吉方位" in result.categories
        assert "総合運勢" in result.categories

        # テンプレート内容を確認
        template = result.templates[0]
        assert template.id is not None
        assert template.category is not None
        assert template.pattern_name is not None
        assert template.title is not None
        assert template.content is not None
        assert isinstance(template.keywords, list)
        assert template.usage_count >= 0
        assert isinstance(template.is_active, bool)

    def test_get_kantei_templates_category_filter(
        self,
        template_service: TemplateService
    ):
        """カテゴリフィルター付きテンプレート取得"""
        result = template_service.get_kantei_templates(category="九星気学")

        # カテゴリフィルターが適用されていることを確認
        for template in result.templates:
            assert template.category == "九星気学"

    def test_get_kantei_templates_limit(
        self,
        template_service: TemplateService
    ):
        """制限数付きテンプレート取得"""
        limit = 2
        result = template_service.get_kantei_templates(limit=limit)

        # 制限数が適用されていることを確認
        assert len(result.templates) <= limit

    def test_get_kantei_templates_active_only(
        self,
        template_service: TemplateService
    ):
        """アクティブテンプレートのみ取得"""
        result = template_service.get_kantei_templates(active_only=True)

        # アクティブフラグが適用されていることを確認
        for template in result.templates:
            assert template.is_active is True

    # =========================================
    # その他のビジネスロジックテスト
    # =========================================

    def test_validate_file_upload_valid(
        self,
        template_service: TemplateService
    ):
        """ファイルアップロード事前検証（成功）"""
        result = template_service.validate_file_upload("test.png", 1024)
        assert result is True

        result = template_service.validate_file_upload("test.JPG", 1024)
        assert result is True

    def test_validate_file_upload_invalid(
        self,
        template_service: TemplateService
    ):
        """ファイルアップロード事前検証（失敗）"""
        # ファイル名なし
        result = template_service.validate_file_upload("", 1024)
        assert result is False

        # 無効な拡張子
        result = template_service.validate_file_upload("test.txt", 1024)
        assert result is False

        # ファイルサイズ上限超過
        result = template_service.validate_file_upload("test.png", 3 * 1024 * 1024)
        assert result is False

    def test_get_all_template_settings(
        self,
        template_service: TemplateService,
        test_user: User
    ):
        """全テンプレート設定一覧取得（管理者用）"""
        # テスト用設定を作成
        template_service.get_template_settings(test_user.id)

        result = template_service.get_all_template_settings(skip=0, limit=10)

        # 結果を確認
        assert isinstance(result, list)
        assert len(result) >= 1

        # 作成した設定が含まれているか確認
        user_settings = [s for s in result if s.user_id == test_user.id]
        assert len(user_settings) == 1