import os
from dotenv import load_dotenv
import logging
from utils.email_sender import EmailSender

# ロギングの設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_email_sending():
    try:
        # 環境変数の読み込み
        load_dotenv()
        
        # 設定値の確認
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = os.getenv('SMTP_PORT')
        username = os.getenv('SMTP_USERNAME')
        password = os.getenv('SMTP_PASSWORD')
        
        logger.debug(f"SMTP Settings:")
        logger.debug(f"Server: {smtp_server}")
        logger.debug(f"Port: {smtp_port}")
        logger.debug(f"Username: {username}")
        logger.debug(f"Password: {'*' * len(password) if password else 'Not set'}")
        
        # EmailSenderの初期化
        email_sender = EmailSender(
            smtp_server=smtp_server,
            smtp_port=int(smtp_port),
            username=username,
            password=password
        )
        
        # テストメールの送信
        test_recipient = username  # 自分自身にテストメールを送信
        subject = "メール送信テスト"
        body = """
        これはテストメールです。
        メール送信機能の動作確認を行っています。
        """
        
        logger.debug(f"Attempting to send test email to: {test_recipient}")
        email_sender.send_email(test_recipient, subject, body)
        logger.debug("Test email sent successfully")
        
    except Exception as e:
        logger.error(f"Error in test_email_sending: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    test_email_sending()