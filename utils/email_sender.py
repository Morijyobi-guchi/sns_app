import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import string
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# 環境変数の読み込み
load_dotenv()

# ロギングの設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self, smtp_server=None, smtp_port=None, username=None, password=None):
        """
        EmailSenderの初期化。引数が与えられない場合は環境変数から読み込む
        """
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER')
        self.smtp_port = int(smtp_port or os.getenv('SMTP_PORT', 587))
        self.username = username or os.getenv('SMTP_USERNAME')
        self.password = password or os.getenv('SMTP_PASSWORD')

        # 必要な設定が揃っているか確認
        if not all([self.smtp_server, self.smtp_port, self.username, self.password]):
            error_msg = "Missing email configuration. Please check your .env file or constructor arguments."
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.debug(f"EmailSender initialized with server: {self.smtp_server}:{self.smtp_port}")

    @staticmethod
    def generate_activation_code(length=32):
        """アクティベーションコードを生成"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def send_email(self, to_email, subject, body):
        """汎用的なメール送信メソッド"""
        logger.debug(f"Preparing to send email to: {to_email}")
        
        try:
            message = MIMEMultipart()
            message["From"] = self.username
            message["To"] = to_email
            message["Subject"] = subject
            
            message.attach(MIMEText(body, "plain", "utf-8"))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.set_debuglevel(1)
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(message)
                
            logger.debug(f"Email sent successfully to: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}", exc_info=True)
            raise

    def send_activation_email(self, to_email, activation_code):
        """アクティベーションメールを送信"""
        logger.debug(f"Preparing to send activation email to: {to_email}")
        
        # 有効期限を24時間後に設定
        expiration_time = datetime.utcnow() + timedelta(hours=24)
        expiration_str = expiration_time.strftime('%Y-%m-%d %H:%M:%S UTC')

        # メール本文
        body = f"""
        ご登録ありがとうございます。

        以下のコードを使用してアカウントを有効化してください：
        {activation_code}

        このコードの有効期限: {expiration_str}

        このメールに心当たりがない場合は、無視していただいて構いません。
        """
        
        return self.send_email(to_email, "アカウントの有効化", body)

    def send_follow_notification(self, to_email, follower_username):
        """フォロー通知メールを送信"""
        body = f"""
        {follower_username}さんがあなたをフォローしました。

        プロフィールを確認するにはアプリにログインしてください。
        """
        
        return self.send_email(to_email, "新しいフォロワー", body)

    def send_password_reset_email(self, to_email, reset_code):
        """パスワードリセットメールを送信"""
        # 有効期限を1時間後に設定
        expiration_time = datetime.utcnow() + timedelta(hours=1)
        expiration_str = expiration_time.strftime('%Y-%m-%d %H:%M:%S UTC')
        
        body = f"""
        パスワードリセットのリクエストを受け付けました。

        以下のコードを使用してパスワードをリセットしてください：
        {reset_code}

        このコードの有効期限: {expiration_str}

        このリクエストに心当たりがない場合は、このメールを無視してください。
        """
        
        return self.send_email(to_email, "パスワードリセット", body)

    def send_welcome_email(self, to_email, username):
        """アカウント有効化後のウェルカムメールを送信"""
        body = f"""
        {username}さん、

        アカウントの有効化が完了しました！
        これからSNSアプリをお楽しみください。

        早速、以下のことから始めてみましょう：
        - プロフィールを設定する
        - 最初の投稿を作成する
        - 興味のあるユーザーをフォローする

        ご不明な点がございましたら、お気軽にお問い合わせください。
        """
        
        return self.send_email(to_email, "ようこそ！", body)

    def __str__(self):
        """EmailSenderオブジェクトの文字列表現"""
        return f"EmailSender(server={self.smtp_server}, port={self.smtp_port}, username={self.username})"

    def __repr__(self):
        """EmailSenderオブジェクトの開発者向け文字列表現"""
        return self.__str__()
    
    def send_verification_email(self, email, code):
        """認証メールの送信"""
        subject = "メールアドレス認証"
        body = f"""
        メールアドレス認証を完了してください。
        
        認証コード: {code}
        
        このコードは24時間有効です。
        セキュリティのため、このメールは他人に共有しないでください。
        """
        
        self.send_email(email, subject, body)