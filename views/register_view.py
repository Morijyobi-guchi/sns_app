import tkinter as tk
from tkinter import ttk, messagebox
from models.user import User
from utils.email_sender import EmailSender
import os
from dotenv import load_dotenv
import logging
import smtplib

# ロガーの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 環境変数の読み込み
load_dotenv()

# SMTP設定を環境変数から取得
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'y.mukaiguchi.sys24@morijyobi.ac.jp')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')  # .envファイルから取得

class RegisterView(tk.Frame):
    def __init__(self, parent, session_manager, show_login):
        super().__init__(parent)
        self.session_manager = session_manager
        self.show_login = show_login
        self.user_model = User()
        self.email_sender = EmailSender(SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD)
        self.create_widgets()


    def register_user(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # 入力チェック
        if not all([username, email, password, confirm_password]):
            messagebox.showerror("エラー", "全ての項目を入力してください")
            return

        if password != confirm_password:
            messagebox.showerror("エラー", "パスワードが一致しません")
            return

        try:
            # ユーザー登録処理
            user_id = self.user_model.create_user(username, email, password)
            messagebox.showinfo("成功", "ユーザー登録が完了しました")
            # ログイン画面に遷移
            self.show_login()
        except Exception as e:
            messagebox.showerror("エラー", str(e))

    def create_widgets(self):
        self.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(self, text="新規登録", font=('Helvetica', 18, 'bold'))
        title_label.pack(pady=(20, 10))

        form_frame = ttk.Frame(self)
        form_frame.pack(pady=(20, 10))

        username_label = ttk.Label(form_frame, text="ユーザー名:")
        username_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.username_entry = ttk.Entry(form_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        email_label = ttk.Label(form_frame, text="メールアドレス:")
        email_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.email_entry = ttk.Entry(form_frame)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)

        password_label = ttk.Label(form_frame, text="パスワード:")
        password_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.password_entry = ttk.Entry(form_frame, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)

        # register_buttonのcommandを handle_register に変更
        register_button = ttk.Button(self, text="登録", command=self.handle_register)
        register_button.pack(pady=(10, 20))

        back_button = ttk.Button(self, text="戻る", command=self.show_login)
        back_button.pack()
        
    def handle_register(self):
        """ユーザー登録処理"""
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        # 入力チェック
        if not all([username, email, password]):
            messagebox.showwarning("警告", "すべてのフィールドを入力してください。")
            return

        try:
            # アクティベーションコードの生成
            activation_code = EmailSender.generate_activation_code()
            
            logger.info(f"Attempting to create user: {username}")
            # ユーザーの作成（アクティベーションコードも保存）
            user_id = self.user_model.create_user(
                username=username,
                email=email,
                password=password,
                activation_code=activation_code
            )
            logger.info(f"User created successfully with ID: {user_id}")

            try:
                logger.info(f"Attempting to send activation email to: {email}")
                logger.debug(f"SMTP Settings - Server: {self.email_sender.smtp_server}, Port: {self.email_sender.smtp_port}")
                
                # SMTPの接続テスト
                try:
                    with smtplib.SMTP(self.email_sender.smtp_server, self.email_sender.smtp_port, timeout=10) as server:
                        server.starttls()
                        logger.info("SMTP TLS connection successful")
                        server.login(self.email_sender.username, self.email_sender.password)
                        logger.info("SMTP login successful")
                except smtplib.SMTPAuthenticationError as auth_error:
                    logger.error(f"SMTP Authentication failed: {str(auth_error)}")
                    raise
                except Exception as conn_error:
                    logger.error(f"SMTP Connection error: {str(conn_error)}")
                    raise

                # アクティベーションメールの送信
                self.email_sender.send_activation_email(
                    to_email=email,
                    activation_code=activation_code
                )
                logger.info("Activation email sent successfully")
                
                messagebox.showinfo(
                    "登録完了",
                    "アカウントの登録が完了しました。\n"
                    "登録したメールアドレスに確認メールを送信しましたので、"
                    "メール内のリンクをクリックしてアカウントを有効化してください。"
                )

            except smtplib.SMTPAuthenticationError as auth_error:
                logger.error(f"SMTP認証エラー: {str(auth_error)}", exc_info=True)
                messagebox.showerror(
                    "メール送信エラー",
                    "メールサーバーの認証に失敗しました。\n"
                    "アプリパスワードが正しく設定されているか確認してください。"
                )
            except Exception as e:
                logger.error(f"メール送信エラー: {str(e)}", exc_info=True)
                messagebox.showwarning(
                    "警告",
                    "ユーザー登録は完了しましたが、確認メールの送信に失敗しました。\n"
                    f"エラー詳細: {str(e)}\n"
                    "管理者に連絡してください。"
                )
            finally:
                # 登録自体は成功しているので、ログイン画面に戻る
                self.show_login()

        except Exception as e:
            # ユーザー登録自体の失敗
            logger.error(f"ユーザー登録エラー: {str(e)}", exc_info=True)
            messagebox.showerror("エラー", f"ユーザー登録に失敗しました: {str(e)}")