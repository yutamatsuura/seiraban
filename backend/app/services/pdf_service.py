"""
PDF生成サービス - ReportLabを使用した鑑定書PDF生成
Phase S-2b担当: PDF生成・管理・ダウンロード機能

機能:
- ReportLabによるPDF鑑定書生成
- TemplateSettings連携（ロゴ・屋号反映）
- 実データでの動作保証
- セキュアなファイル管理

技術仕様:
- ReportLab PDF生成
- SQLAlchemy ORM
- NEON PostgreSQL接続
- 実データテスト必須
"""

import os
import io
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# ReportLab PDF生成
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# 内部依存
from ..models import KanteiRecord, TemplateSettings
from ..schemas.pdf import (
    PDFGenerationRequest,
    PDFGenerationResponse,
    PDFDownloadResponse,
    PDFStatusEnum
)

class PDFServiceError(Exception):
    """PDF生成サービス専用例外"""
    pass

class PDFGenerationService:
    """PDF生成メインサービス"""

    def __init__(self, storage_path: str = "/tmp/pdf_storage"):
        """
        PDFサービス初期化

        Args:
            storage_path: PDFファイル保存パス
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # ReportLabスタイル設定
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """カスタムスタイルの設定"""
        # 日本語対応フォント設定
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # システムフォントを使用（Hiragino Sans等）
        # 本番環境では適切な日本語フォントパスを設定

        # カスタムスタイル定義
        self.styles.add(ParagraphStyle(
            name='KanteiTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#2C3E50')
        ))

        self.styles.add(ParagraphStyle(
            name='KanteiHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            alignment=TA_LEFT,
            spaceAfter=12,
            textColor=colors.HexColor('#34495E')
        ))

        self.styles.add(ParagraphStyle(
            name='KanteiBody',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=8,
            leftIndent=20
        ))

    def generate_pdf(
        self,
        db: Session,
        request: PDFGenerationRequest,
        user_id: int
    ) -> PDFGenerationResponse:
        """
        PDF鑑定書生成メイン処理

        Args:
            db: データベースセッション
            request: PDF生成リクエスト
            user_id: ユーザーID

        Returns:
            PDFGenerationResponse: 生成結果

        Raises:
            PDFServiceError: PDF生成エラー
        """
        try:
            # 鑑定記録取得
            kantei_record = self._get_kantei_record(db, request.kantei_record_id, user_id)

            # テンプレート設定取得
            template_settings = None
            if request.use_template_settings:
                template_settings = self._get_template_settings(db, user_id)

            # PDF生成実行
            pdf_path, file_size = self._create_pdf_document(
                kantei_record,
                template_settings,
                request.custom_message
            )

            # データベース更新
            current_time = datetime.now()
            kantei_record.pdf_url = str(pdf_path)
            kantei_record.pdf_file_size = file_size
            kantei_record.pdf_generated_at = current_time
            kantei_record.status = "completed"

            db.commit()

            return PDFGenerationResponse(
                success=True,
                pdf_id=kantei_record.id,
                pdf_url=str(pdf_path),
                file_size=file_size,
                page_count=self._count_pdf_pages(pdf_path),
                generated_at=current_time
            )

        except SQLAlchemyError as e:
            db.rollback()
            raise PDFServiceError(f"データベースエラー: {str(e)}")
        except Exception as e:
            db.rollback()
            raise PDFServiceError(f"PDF生成エラー: {str(e)}")

    def _get_kantei_record(self, db: Session, record_id: int, user_id: int) -> KanteiRecord:
        """鑑定記録取得"""
        record = db.query(KanteiRecord).filter(
            KanteiRecord.id == record_id,
            KanteiRecord.user_id == user_id
        ).first()

        if not record:
            raise PDFServiceError(f"鑑定記録 ID {record_id} が見つかりません")

        return record

    def _get_template_settings(self, db: Session, user_id: int) -> Optional[TemplateSettings]:
        """テンプレート設定取得"""
        return db.query(TemplateSettings).filter(
            TemplateSettings.user_id == user_id
        ).first()

    def _create_pdf_document(
        self,
        kantei_record: KanteiRecord,
        template_settings: Optional[TemplateSettings],
        custom_message: Optional[str]
    ) -> Tuple[Path, int]:
        """
        PDF文書作成

        Returns:
            Tuple[Path, int]: (PDF保存パス, ファイルサイズ)
        """
        # ファイル名生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"kantei_{kantei_record.id}_{timestamp}.pdf"
        pdf_path = self.storage_path / filename

        # PDF文書作成
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # 文書内容構築
        story = []

        # ヘッダー部分（ロゴ・屋号）
        self._add_header(story, template_settings)

        # タイトル
        story.append(Paragraph("鑑定書", self.styles['KanteiTitle']))
        story.append(Spacer(1, 20))

        # クライアント情報
        self._add_client_info(story, kantei_record)

        # 鑑定結果
        self._add_kantei_results(story, kantei_record)

        # カスタムメッセージ
        if custom_message:
            self._add_custom_message(story, custom_message)

        # フッター
        self._add_footer(story, template_settings)

        # PDF生成実行
        doc.build(story)

        # ファイルサイズ取得
        file_size = pdf_path.stat().st_size

        return pdf_path, file_size

    def _add_header(self, story: list, template_settings: Optional[TemplateSettings]):
        """ヘッダー部分追加"""
        if template_settings and template_settings.logo_url:
            # ロゴ画像追加（ローカルファイルの場合）
            try:
                if Path(template_settings.logo_url).exists():
                    logo = Image(template_settings.logo_url, width=2*inch, height=1*inch)
                    story.append(logo)
                    story.append(Spacer(1, 10))
            except Exception:
                # ロゴ読み込み失敗時はスキップ
                pass

        # 事業者情報
        if template_settings:
            business_info = f"""
            <b>{template_settings.business_name or '鑑定事務所'}</b><br/>
            運営者: {template_settings.operator_name or ''}
            """
            story.append(Paragraph(business_info, self.styles['Normal']))
            story.append(Spacer(1, 20))

    def _add_client_info(self, story: list, kantei_record: KanteiRecord):
        """クライアント情報追加"""
        story.append(Paragraph("お客様情報", self.styles['KanteiHeader']))

        client_info = kantei_record.client_info or {}

        client_data = [
            ['お名前', kantei_record.client_name],
            ['生年月日', client_info.get('birth_date', 'なし')],
            ['性別', client_info.get('gender', 'なし')],
            ['出生時刻', client_info.get('birth_time', 'なし')],
            ['出生地', client_info.get('birth_place', 'なし')]
        ]

        table = Table(client_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(table)
        story.append(Spacer(1, 20))

    def _add_kantei_results(self, story: list, kantei_record: KanteiRecord):
        """鑑定結果追加"""
        story.append(Paragraph("鑑定結果", self.styles['KanteiHeader']))

        calculation_result = kantei_record.calculation_result or {}

        # 九星気学結果
        if 'kyusei_kigaku' in calculation_result:
            kyusei_data = calculation_result['kyusei_kigaku']
            kyusei_text = f"""
            <b>九星気学・吉方位の鑑定結果:</b><br/>
            本命星: {kyusei_data.get('honmei_star', 'なし')}<br/>
            月命星: {kyusei_data.get('gekkei_star', 'なし')}<br/>
            日命星: {kyusei_data.get('nichimei_star', 'なし')}<br/>
            運勢: {kyusei_data.get('fortune_summary', 'なし')}
            """
            story.append(Paragraph(kyusei_text, self.styles['KanteiBody']))
            story.append(Spacer(1, 15))

        # 姓名判断結果
        if 'seimei_handan' in calculation_result:
            seimei_data = calculation_result['seimei_handan']
            seimei_text = f"""
            <b>姓名判断結果:</b><br/>
            天格: {seimei_data.get('tenkaku', 'なし')}画<br/>
            人格: {seimei_data.get('jinkaku', 'なし')}画<br/>
            地格: {seimei_data.get('chikaku', 'なし')}画<br/>
            総格: {seimei_data.get('soukaku', 'なし')}画<br/>
            総合評価: {seimei_data.get('overall_rating', 'なし')}
            """
            story.append(Paragraph(seimei_text, self.styles['KanteiBody']))
            story.append(Spacer(1, 15))

        # 吉方位結果
        if 'kichihoui' in calculation_result:
            kichi_data = calculation_result['kichihoui']
            kichi_text = f"""
            <b>吉方位鑑定結果:</b><br/>
            今月の吉方位: {kichi_data.get('this_month', 'なし')}<br/>
            今年の吉方位: {kichi_data.get('this_year', 'なし')}<br/>
            推奨行動: {kichi_data.get('recommendations', 'なし')}
            """
            story.append(Paragraph(kichi_text, self.styles['KanteiBody']))

    def _add_custom_message(self, story: list, custom_message: str):
        """カスタムメッセージ追加"""
        story.append(Spacer(1, 20))
        story.append(Paragraph("特別メッセージ", self.styles['KanteiHeader']))
        story.append(Paragraph(custom_message, self.styles['KanteiBody']))

    def _add_footer(self, story: list, template_settings: Optional[TemplateSettings]):
        """フッター追加"""
        story.append(Spacer(1, 30))

        footer_text = f"""
        <i>この鑑定書は {datetime.now().strftime('%Y年%m月%d日')} に作成されました。</i><br/>
        """

        if template_settings:
            footer_text += f"<i>{template_settings.business_name or '鑑定事務所'} - {template_settings.operator_name or ''}</i>"

        story.append(Paragraph(footer_text, self.styles['Normal']))

    def _count_pdf_pages(self, pdf_path: Path) -> int:
        """PDFページ数取得"""
        try:
            # 簡易実装：ファイルサイズベースの推定
            file_size = pdf_path.stat().st_size
            # 平均的なページサイズを基準に推定（実際はPDFライブラリで正確に取得）
            estimated_pages = max(1, file_size // 100000)  # 100KB per page estimate
            return min(estimated_pages, 10)  # 最大10ページに制限
        except Exception:
            return 1

    def get_pdf_download_info(
        self,
        db: Session,
        kantei_record_id: int,
        user_id: int
    ) -> PDFDownloadResponse:
        """
        PDFダウンロード情報取得

        Args:
            db: データベースセッション
            kantei_record_id: 鑑定記録ID
            user_id: ユーザーID

        Returns:
            PDFDownloadResponse: ダウンロード情報
        """
        try:
            # 鑑定記録取得
            kantei_record = self._get_kantei_record(db, kantei_record_id, user_id)

            if not kantei_record.pdf_url:
                raise PDFServiceError("PDFが生成されていません")

            # ファイル存在確認
            pdf_path = Path(kantei_record.pdf_url)
            if not pdf_path.exists():
                raise PDFServiceError("PDFファイルが見つかりません")

            # ダウンロード情報生成
            current_time = datetime.now()
            expires_at = current_time + timedelta(hours=1)

            # 安全なファイル名生成
            safe_client_name = kantei_record.client_name.replace(" ", "_").replace("　", "_")
            file_name = f"{safe_client_name}様_鑑定書_{current_time.strftime('%Y%m%d')}.pdf"

            # セキュアダウンロードURL生成（簡易実装）
            download_url = f"/api/kantei/secure-download/{kantei_record_id}?token=temp_token_{current_time.timestamp()}"

            return PDFDownloadResponse(
                success=True,
                file_name=file_name,
                file_size=kantei_record.pdf_file_size or 0,
                content_type="application/pdf",
                download_url=download_url,
                expires_at=expires_at
            )

        except Exception as e:
            raise PDFServiceError(f"ダウンロード情報取得エラー: {str(e)}")

    def get_pdf_status(
        self,
        db: Session,
        kantei_record_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        PDF処理ステータス取得

        Returns:
            Dict: ステータス情報
        """
        try:
            kantei_record = self._get_kantei_record(db, kantei_record_id, user_id)

            # ステータス判定
            if kantei_record.pdf_url and Path(kantei_record.pdf_url).exists():
                status = PDFStatusEnum.COMPLETED
            else:
                status = PDFStatusEnum.PENDING

            return {
                "kantei_record_id": kantei_record_id,
                "pdf_status": status,
                "pdf_url": kantei_record.pdf_url,
                "error_message": None,
                "updated_at": kantei_record.updated_at
            }

        except Exception as e:
            return {
                "kantei_record_id": kantei_record_id,
                "pdf_status": PDFStatusEnum.FAILED,
                "pdf_url": None,
                "error_message": str(e),
                "updated_at": datetime.now()
            }

    def cleanup_old_pdfs(self, days_old: int = 30):
        """古いPDFファイルのクリーンアップ"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days_old)

            for pdf_file in self.storage_path.glob("*.pdf"):
                file_time = datetime.fromtimestamp(pdf_file.stat().st_mtime)
                if file_time < cutoff_time:
                    pdf_file.unlink()

        except Exception as e:
            raise PDFServiceError(f"クリーンアップエラー: {str(e)}")


# サービスインスタンス（シングルトン）
pdf_service = PDFGenerationService()


def get_pdf_service() -> PDFGenerationService:
    """PDF生成サービス取得"""
    return pdf_service