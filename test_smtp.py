import os
from dotenv import load_dotenv
import smtplib

load_dotenv()

def test_smtp_connection():
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')

    print(f"Testing SMTP connection to {smtp_server}:{smtp_port}")
    print(f"Username: {smtp_username}")
    print(f"Password length: {len(smtp_password) if smtp_password else 'No password set'}")

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            print("SMTP connection and authentication successful!")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_smtp_connection()