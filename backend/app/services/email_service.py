"""
メール送信サービス - Phase S-3a実装

履歴管理における鑑定書再送信機能のためのメール送信サービス

機能:
- PDF添付メール送信
- 送信結果の詳細情報返却
- 外部メール送信サービス（SendGrid等）との連携準備
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime


class EmailService:
    """メール送信サービス

    現在は開発用のモック実装。
    本番環境では SendGrid, Mailgun, AWS SES 等の実際のメール送信サービスと連携。
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.provider = "mock_sendgrid"  # 開発用

        # 本番設定（環境変数から取得予定）
        self.api_key = os.getenv("SENDGRID_API_KEY", "dev-mock-key")
        self.from_email = os.getenv("MAIL_FROM", "noreply@kantei-system.com")

    def send_kantei_email(
        self,
        recipient_email: str,
        sender_name: str,
        client_name: str,
        pdf_url: str,
        custom_message: Optional[str] = None,
        kantei_record_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        鑑定書添付メール送信

        Args:
            recipient_email: 送信先メールアドレス
            sender_name: 送信者名
            client_name: クライアント名
            pdf_url: PDFファイルのURL
            custom_message: カスタムメッセージ（任意）
            kantei_record_id: 鑑定記録ID（ログ用）

        Returns:
            Dict: 送信結果
            {
                "success": bool,
                "message_id": str,
                "provider": str,
                "sent_at": datetime,
                "error": str (失敗時のみ)
            }
        """
        try:
            # 件名生成
            subject = f"鑑定書をお送りします（{client_name}様）"

            # メール本文生成
            body = self._generate_email_body(
                client_name=client_name,
                sender_name=sender_name,
                custom_message=custom_message
            )

            # 現在は開発用モック実装
            if self.provider == "mock_sendgrid":
                return self._mock_send_email(
                    recipient_email=recipient_email,
                    subject=subject,
                    body=body,
                    pdf_url=pdf_url,
                    kantei_record_id=kantei_record_id
                )

            # 本番環境では実際のメール送信サービスを使用
            # return self._sendgrid_send_email(...)
            # return self._mailgun_send_email(...)
            # return self._aws_ses_send_email(...)

        except Exception as e:
            self.logger.error(f"メール送信エラー: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.provider
            }

    def _generate_email_body(
        self,
        client_name: str,
        sender_name: str,
        custom_message: Optional[str] = None
    ) -> str:
        """
        メール本文生成

        Args:
            client_name: クライアント名
            sender_name: 送信者名
            custom_message: カスタムメッセージ

        Returns:
            str: メール本文
        """
        base_message = f"""
{client_name} 様

いつもお世話になっております。
{sender_name} です。

鑑定書をお送りいたします。
添付のPDFファイルをご確認ください。
"""

        if custom_message:
            base_message += f"\n\n【追加メッセージ】\n{custom_message}\n"

        base_message += f"""

ご不明な点がございましたら、お気軽にお問い合わせください。

---
{sender_name}
鑑定システム v2
"""

        return base_message.strip()

    def _mock_send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        pdf_url: str,
        kantei_record_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        開発用モックメール送信

        実際にはメールを送信せず、成功レスポンスを返却。
        ログには送信内容を記録。

        Args:
            recipient_email: 送信先
            subject: 件名
            body: 本文
            pdf_url: PDF URL
            kantei_record_id: 鑑定記録ID

        Returns:
            Dict: モック送信結果
        """
        # モックメッセージID生成
        timestamp = int(datetime.now().timestamp())
        mock_message_id = f"mock_msg_{timestamp}_{kantei_record_id or 'unknown'}"

        # ログ出力（開発用）
        self.logger.info(f"""
=== 模擬メール送信 ===
To: {recipient_email}
Subject: {subject}
PDF: {pdf_url}
Body: {body[:100]}...
Message ID: {mock_message_id}
========================
""")

        # PDFファイルの存在確認（モック）
        if not pdf_url:
            raise ValueError("PDFファイルのURLが指定されていません")

        # 成功レスポンス
        return {
            "success": True,
            "message_id": mock_message_id,
            "provider": "mock_sendgrid",
            "sent_at": datetime.now(),
            "recipient": recipient_email,
            "subject": subject
        }

    # =========================================
    # 本番用メール送信実装（準備）
    # =========================================

    def _sendgrid_send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        pdf_url: str
    ) -> Dict[str, Any]:
        """
        SendGrid経由でのメール送信（本番用）

        Note: 実装時に sendgrid ライブラリをインストール:
        pip install sendgrid

        Args:
            recipient_email: 送信先
            subject: 件名
            body: 本文
            pdf_url: PDF URL

        Returns:
            Dict: 送信結果
        """
        # TODO: 本番実装時に有効化
        """
        import sendgrid
        from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType

        sg = sendgrid.SendGridAPIClient(api_key=self.api_key)

        # PDF添付ファイル準備
        # (実際はpdf_urlからファイルをダウンロードしてbase64エンコード)

        message = Mail(
            from_email=self.from_email,
            to_emails=recipient_email,
            subject=subject,
            html_content=body.replace('\n', '<br>')
        )

        # PDF添付
        # message.attachment = Attachment(...)

        response = sg.send(message)

        return {
            "success": True,
            "message_id": response.headers.get('X-Message-Id'),
            "provider": "sendgrid",
            "sent_at": datetime.now()
        }
        """
        pass

    def _aws_ses_send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        pdf_url: str
    ) -> Dict[str, Any]:
        """
        AWS SES経由でのメール送信（本番用）

        Note: 実装時に boto3 ライブラリをインストール:
        pip install boto3

        Args:
            recipient_email: 送信先
            subject: 件名
            body: 本文
            pdf_url: PDF URL

        Returns:
            Dict: 送信結果
        """
        # TODO: 本番実装時に有効化
        """
        import boto3
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.application import MIMEApplication

        ses_client = boto3.client('ses', region_name='ap-northeast-1')

        # MIME メッセージ作成
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # 本文追加
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # PDF添付（実際はpdf_urlからダウンロード）
        # with open(pdf_file_path, 'rb') as f:
        #     attachment = MIMEApplication(f.read())
        #     attachment.add_header('Content-Disposition', 'attachment', filename='kantei.pdf')
        #     msg.attach(attachment)

        response = ses_client.send_raw_email(
            Source=self.from_email,
            Destinations=[recipient_email],
            RawMessage={'Data': msg.as_string()}
        )

        return {
            "success": True,
            "message_id": response['MessageId'],
            "provider": "aws_ses",
            "sent_at": datetime.now()
        }
        """
        pass

    # =========================================
    # ユーティリティメソッド
    # =========================================

    def validate_email_address(self, email: str) -> bool:
        """
        メールアドレスの簡易バリデーション

        Args:
            email: メールアドレス

        Returns:
            bool: 有効かどうか
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def get_email_template(self, template_name: str) -> str:
        """
        メールテンプレート取得

        Args:
            template_name: テンプレート名

        Returns:
            str: テンプレート内容
        """
        templates = {
            "kantei_delivery": """
{client_name} 様

いつもお世話になっております。
{sender_name} です。

鑑定書をお送りいたします。
添付のPDFファイルをご確認ください。

{custom_message}

ご不明な点がございましたら、お気軽にお問い合わせください。

---
{sender_name}
鑑定システム v2
""",
            "kantei_resend": """
{client_name} 様

再度鑑定書をお送りいたします。
{sender_name} です。

{custom_message}

添付のPDFファイルをご確認ください。

---
{sender_name}
鑑定システム v2
"""
        }

        return templates.get(template_name, templates["kantei_delivery"])