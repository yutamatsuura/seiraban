"""
履歴管理サービス層 - Phase S-3a実装

対象エンドポイント:
- 4.1 `/api/kantei/history` GET - 鑑定履歴一覧取得
- 4.2 `/api/kantei/detail/{id}` GET - 鑑定詳細情報取得
- 4.3 `/api/kantei/resend/{id}` POST - 鑑定書再送信

実装内容:
- 実際のデータベースを使った履歴管理
- ページング・検索機能
- メール再送信機能
- 実データでのビジネスロジック
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, and_
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from ..models import KanteiRecord, EmailHistory, User
from ..schemas.history import (
    KanteiHistoryResponse,
    KanteiHistoryItem,
    KanteiDetailResponse,
    ResendRequest,
    ResendResponse,
    EmailHistoryResponse,
    validate_pagination_params,
    calculate_offset,
    calculate_total_pages
)
from .email_service import EmailService


class HistoryService:
    """履歴管理サービス

    機能:
    - 鑑定履歴の一覧取得（ページング対応）
    - 鑑定詳細情報の取得
    - 鑑定書の再送信
    - メール送信履歴の管理
    """

    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()

    # =========================================
    # 4.1 鑑定履歴一覧取得
    # =========================================

    def get_kantei_history(
        self,
        user_id: int,
        page: int = 1,
        limit: int = 20,
        search_query: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> KanteiHistoryResponse:
        """
        鑑定履歴一覧取得（ページング・検索対応）

        Args:
            user_id: ユーザーID
            page: ページ番号
            limit: 1ページあたりの件数
            search_query: 検索クエリ（クライアント名で検索）
            status_filter: ステータスフィルター

        Returns:
            KanteiHistoryResponse: ページング情報と履歴一覧

        Raises:
            ValueError: パラメータが不正な場合
            Exception: データベースエラー時
        """
        try:
            # パラメータバリデーション
            page, limit = validate_pagination_params(page, limit)
            offset = calculate_offset(page, limit)

            # 基本クエリ
            query = self.db.query(KanteiRecord).filter(
                KanteiRecord.user_id == user_id,
                KanteiRecord.deleted_at.is_(None)
            )

            # 検索条件を追加
            if search_query:
                query = query.filter(
                    KanteiRecord.client_name.ilike(f"%{search_query}%")
                )

            # ステータスフィルター
            if status_filter:
                query = query.filter(KanteiRecord.status == status_filter)

            # 総件数取得
            total = query.count()

            # ページング適用とデータ取得
            kantei_records = query.order_by(
                desc(KanteiRecord.created_at)
            ).offset(offset).limit(limit).all()

            # 各レコードのメール送信統計を取得
            history_items = []
            for record in kantei_records:
                email_stats = self._get_email_stats(record.id)

                history_items.append(KanteiHistoryItem(
                    id=record.id,
                    client_name=record.client_name,
                    client_email=record.client_email,
                    status=record.status,
                    custom_message=record.custom_message,
                    pdf_url=record.pdf_url,
                    created_at=record.created_at,
                    updated_at=record.updated_at,
                    email_count=email_stats["count"],
                    last_sent_at=email_stats["last_sent_at"]
                ))

            # 総ページ数計算
            total_pages = calculate_total_pages(total, limit)

            return KanteiHistoryResponse(
                total=total,
                page=page,
                limit=limit,
                total_pages=total_pages,
                items=history_items
            )

        except Exception as e:
            raise Exception(f"鑑定履歴の取得に失敗しました: {str(e)}")

    def _get_email_stats(self, kantei_record_id: int) -> Dict[str, Any]:
        """
        指定された鑑定記録のメール送信統計を取得

        Args:
            kantei_record_id: 鑑定記録ID

        Returns:
            Dict: メール送信統計 {"count": int, "last_sent_at": datetime}
        """
        email_count = self.db.query(func.count(EmailHistory.id)).filter(
            EmailHistory.kantei_record_id == kantei_record_id,
            EmailHistory.status == "sent"
        ).scalar() or 0

        last_sent = self.db.query(func.max(EmailHistory.sent_at)).filter(
            EmailHistory.kantei_record_id == kantei_record_id,
            EmailHistory.status == "sent"
        ).scalar()

        return {
            "count": email_count,
            "last_sent_at": last_sent
        }

    # =========================================
    # 4.2 鑑定詳細情報取得
    # =========================================

    def get_kantei_detail(self, kantei_id: int, user_id: int) -> KanteiDetailResponse:
        """
        鑑定詳細情報取得

        Args:
            kantei_id: 鑑定記録ID
            user_id: ユーザーID（権限確認）

        Returns:
            KanteiDetailResponse: 鑑定詳細情報

        Raises:
            ValueError: 鑑定記録が見つからない場合
            Exception: データベースエラー時
        """
        try:
            # 鑑定記録取得（権限チェック含む）
            kantei_record = self.db.query(KanteiRecord).filter(
                and_(
                    KanteiRecord.id == kantei_id,
                    KanteiRecord.user_id == user_id,
                    KanteiRecord.deleted_at.is_(None)
                )
            ).options(joinedload(KanteiRecord.email_history)).first()

            if not kantei_record:
                raise ValueError("指定された鑑定記録が見つかりません")

            # メール履歴を変換
            email_history = []
            for email in kantei_record.email_history:
                email_history.append(EmailHistoryResponse(
                    id=email.id,
                    kantei_record_id=email.kantei_record_id,
                    recipient_email=email.recipient_email,
                    sender_name=email.sender_name,
                    subject=email.subject,
                    message_content=email.message_content,
                    message_id=email.message_id,
                    provider=email.provider,
                    status=email.status,
                    error_message=email.error_message,
                    sent_at=email.sent_at,
                    delivered_at=email.delivered_at,
                    created_at=email.created_at,
                    updated_at=email.updated_at
                ))

            return KanteiDetailResponse(
                id=kantei_record.id,
                user_id=kantei_record.user_id,
                client_name=kantei_record.client_name,
                client_email=kantei_record.client_email,
                client_info=kantei_record.client_info,
                calculation_result=kantei_record.calculation_result,
                pdf_url=kantei_record.pdf_url,
                pdf_file_size=kantei_record.pdf_file_size,
                pdf_generated_at=kantei_record.pdf_generated_at,
                status=kantei_record.status,
                custom_message=kantei_record.custom_message,
                created_at=kantei_record.created_at,
                updated_at=kantei_record.updated_at,
                email_history=email_history
            )

        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"鑑定詳細情報の取得に失敗しました: {str(e)}")

    # =========================================
    # 4.3 鑑定書再送信
    # =========================================

    def resend_kantei(
        self,
        kantei_id: int,
        user_id: int,
        resend_data: ResendRequest
    ) -> ResendResponse:
        """
        鑑定書再送信

        Args:
            kantei_id: 鑑定記録ID
            user_id: ユーザーID（権限確認）
            resend_data: 再送信データ

        Returns:
            ResendResponse: 送信結果

        Raises:
            ValueError: 鑑定記録が見つからない場合
            Exception: メール送信エラー時
        """
        try:
            # 鑑定記録取得（権限チェック含む）
            kantei_record = self.db.query(KanteiRecord).filter(
                and_(
                    KanteiRecord.id == kantei_id,
                    KanteiRecord.user_id == user_id,
                    KanteiRecord.deleted_at.is_(None)
                )
            ).first()

            if not kantei_record:
                raise ValueError("指定された鑑定記録が見つかりません")

            # PDFファイルが存在するかチェック
            if not kantei_record.pdf_url:
                raise ValueError("PDF鑑定書が生成されていません")

            # ユーザー情報取得（送信者情報用）
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("ユーザー情報が見つかりません")

            # メール送信実行
            email_result = self.email_service.send_kantei_email(
                recipient_email=resend_data.recipient_email,
                sender_name=resend_data.sender_name or user.operator_name or user.business_name,
                client_name=kantei_record.client_name,
                pdf_url=kantei_record.pdf_url,
                custom_message=resend_data.message,
                kantei_record_id=kantei_id
            )

            if not email_result["success"]:
                raise Exception(f"メール送信に失敗しました: {email_result['error']}")

            # メール履歴をデータベースに記録
            email_history = EmailHistory(
                kantei_record_id=kantei_id,
                recipient_email=resend_data.recipient_email,
                sender_name=resend_data.sender_name or user.operator_name or user.business_name,
                subject=f"鑑定書をお送りします（{kantei_record.client_name}様）",
                message_content=resend_data.message,
                message_id=email_result["message_id"],
                provider=email_result["provider"],
                status="sent",
                sent_at=datetime.now()
            )

            self.db.add(email_history)
            self.db.commit()
            self.db.refresh(email_history)

            return ResendResponse(
                success=True,
                message=f"{resend_data.recipient_email} に鑑定書を再送信しました",
                email_history_id=email_history.id,
                message_id=email_result["message_id"],
                sent_at=email_history.sent_at
            )

        except ValueError:
            raise
        except Exception as e:
            self.db.rollback()
            raise Exception(f"鑑定書の再送信に失敗しました: {str(e)}")

    # =========================================
    # 補助メソッド
    # =========================================

    def get_kantei_record_by_id(self, kantei_id: int, user_id: int) -> Optional[KanteiRecord]:
        """
        鑑定記録を取得（権限チェック付き）

        Args:
            kantei_id: 鑑定記録ID
            user_id: ユーザーID

        Returns:
            KanteiRecord: 鑑定記録、または None
        """
        return self.db.query(KanteiRecord).filter(
            and_(
                KanteiRecord.id == kantei_id,
                KanteiRecord.user_id == user_id,
                KanteiRecord.deleted_at.is_(None)
            )
        ).first()

    def get_user_kantei_stats(self, user_id: int) -> Dict[str, Any]:
        """
        ユーザーの鑑定統計情報取得

        Args:
            user_id: ユーザーID

        Returns:
            Dict: 統計情報
        """
        total_kantei = self.db.query(func.count(KanteiRecord.id)).filter(
            KanteiRecord.user_id == user_id,
            KanteiRecord.deleted_at.is_(None)
        ).scalar() or 0

        completed_kantei = self.db.query(func.count(KanteiRecord.id)).filter(
            KanteiRecord.user_id == user_id,
            KanteiRecord.status == "completed",
            KanteiRecord.deleted_at.is_(None)
        ).scalar() or 0

        total_emails = self.db.query(func.count(EmailHistory.id)).join(
            KanteiRecord, EmailHistory.kantei_record_id == KanteiRecord.id
        ).filter(
            KanteiRecord.user_id == user_id,
            EmailHistory.status == "sent"
        ).scalar() or 0

        return {
            "total_kantei": total_kantei,
            "completed_kantei": completed_kantei,
            "total_emails_sent": total_emails,
            "completion_rate": round((completed_kantei / total_kantei * 100) if total_kantei > 0 else 0, 1)
        }