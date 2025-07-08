import tkinter as tk
from tkinter import ttk, messagebox
import secrets
import string
from models.user import User
from utils.email_sender import EmailSender
import logging
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# 環境変数の読み込み
load_dotenv()

# ロギングの設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PasswordResetView:
    def __init__(self, parent, back_to_login_callback):
        self.parent = parent
        self.back_to_login_callback = back_to_login_callback
        self.user_model = User()
        
        # メール送信の初期化
        try:
            self.email_sender = EmailSender(
                smtp_server=os.getenv('SMTP_SERVER'),
                smtp_port=int(os.getenv('SMTP_PORT', 587)),
                username=os.getenv('SMTP_USERNAME'),
                password=os.getenv('SMTP_PASSWORD')
            )
            logger.debug("Email sender initialized for password reset")
        except Exception as e:
            logger.error(f"Failed to initialize email sender: {e}")
            messagebox.showerror("エラー", "メール送信の初期化に失敗しました")
            return

        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        self.create_widgets()
        
        # 確認コードの保持用
        self.verification_data = None

    def create_widgets(self):
        """初期の入力画面を作成（中央寄せ）"""
        # メインフレーム
        self.frame = ttk.Frame(self.parent, padding="20")
        self.frame.grid(row=0, column=0, sticky="")  # sticky="" で中央寄せ
        
        # フレーム内の列を中央寄せに設定
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        # コンテンツを配置するための内部フレーム
        content_frame = ttk.Frame(self.frame)
        content_frame.grid(row=0, column=0, columnspan=2)

        # タイトル
        ttk.Label(
            content_frame,
            text="パスワードリセット",
            font=('Helvetica', 14, 'bold')
        ).pack(pady=10)

        # 説明文
        ttk.Label(
            content_frame,
            text="登録したメールアドレスを入力してください。\n確認コードを送信します。",
            justify=tk.CENTER
        ).pack(pady=10)

        # 入力フィールドのフレーム
        input_frame = ttk.Frame(content_frame)
        input_frame.pack(pady=10)

        # メールアドレス入力
        ttk.Label(input_frame, text="メールアドレス:").pack(pady=5)
        self.email_entry = ttk.Entry(input_frame, width=40)
        self.email_entry.pack(pady=5)

        # ボタンフレーム
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(pady=20)

        # 送信ボタン
        ttk.Button(
            button_frame,
            text="確認コードを送信",
            command=self.send_verification_code
        ).pack(pady=5)

        # 戻るボタン
        ttk.Button(
            button_frame,
            text="ログイン画面に戻る",
            command=self.back_to_login_callback
        ).pack(pady=5)

    def send_verification_code(self):
        """確認コードを生成してメール送信"""
        email = self.email_entry.get().strip()
        
        if not email:
            messagebox.showwarning("警告", "メールアドレスを入力してください")
            return

        try:
            # メールアドレスの存在確認
            user = self.user_model.get_user_by_email(email)
            if not user:
                messagebox.showerror("エラー", "このメールアドレスは登録されていません")
                return

            # 確認コードの生成（32文字）
            verification_code = ''.join(
                secrets.choice(string.ascii_letters + string.digits)
                for _ in range(32)
            )

            # 有効期限の設定（1時間）
            expiration_time = datetime.now() + timedelta(hours=1)
            
            # 確認コード情報の保存
            self.verification_data = {
                'code': verification_code,
                'email': email,
                'user_id': user['user_id'],
                'expiration': expiration_time
            }

            # メール送信
            self.email_sender.send_password_reset_email(email, verification_code)
            
            logger.debug(f"Verification code sent to {email}")
            
            # 確認コード入力画面に切り替え
            self.show_verification_input()

        except Exception as e:
            logger.error(f"Error in send_verification_code: {e}")
            messagebox.showerror("エラー", "確認コードの送信に失敗しました")
            
    def show_verification_input(self):
        """確認コード入力画面の表示（中央寄せ）"""
        for widget in self.frame.winfo_children():
            widget.destroy()

        content_frame = ttk.Frame(self.frame)
        content_frame.grid(row=0, column=0, columnspan=2)

        # タイトル
        ttk.Label(
            content_frame,
            text="確認コードの入力",
            font=('Helvetica', 14, 'bold')
        ).pack(pady=10)

        # 説明文
        ttk.Label(
            content_frame,
            text="メールに送信された確認コードを入力してください。\n有効期限は1時間です。",
            justify=tk.CENTER
        ).pack(pady=10)

        # 入力フィールドのフレーム
        input_frame = ttk.Frame(content_frame)
        input_frame.pack(pady=10)

        # 確認コード入力
        ttk.Label(input_frame, text="確認コード:").pack(pady=5)
        self.code_entry = ttk.Entry(input_frame, width=40)
        self.code_entry.pack(pady=5)

        # ボタンフレーム
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(pady=20)

        # 確認ボタン
        ttk.Button(
            button_frame,
            text="確認",
            command=self.verify_code
        ).pack(pady=5)

        # 戻るボタン
        ttk.Button(
            button_frame,
            text="最初に戻る",
            command=self.create_widgets
        ).pack(pady=5)

    def verify_code(self):
        """確認コードの検証"""
        entered_code = self.code_entry.get().strip()
        
        if not self.verification_data:
            messagebox.showerror("エラー", "確認コードの情報が見つかりません")
            return

        if datetime.now() > self.verification_data['expiration']:
            messagebox.showerror("エラー", "確認コードの有効期限が切れています")
            self.create_widgets()
            return

        if entered_code != self.verification_data['code']:
            messagebox.showerror("エラー", "確認コードが正しくありません")
            return

        # パスワードリセット画面に遷移
        self.show_password_reset()

    def show_password_reset(self):
        """パスワードリセット画面の表示（中央寄せ）"""
        for widget in self.frame.winfo_children():
            widget.destroy()

        content_frame = ttk.Frame(self.frame)
        content_frame.grid(row=0, column=0, columnspan=2)

        # タイトル
        ttk.Label(
            content_frame,
            text="新しいパスワードの設定",
            font=('Helvetica', 14, 'bold')
        ).pack(pady=10)

        # 入力フィールドのフレーム
        input_frame = ttk.Frame(content_frame)
        input_frame.pack(pady=10)

        # パスワード入力
        ttk.Label(input_frame, text="新しいパスワード:").pack(pady=5)
        self.new_password = ttk.Entry(input_frame, show="*", width=40)
        self.new_password.pack(pady=5)

        # パスワード確認
        ttk.Label(input_frame, text="パスワード（確認）:").pack(pady=5)
        self.confirm_password = ttk.Entry(input_frame, show="*", width=40)
        self.confirm_password.pack(pady=5)

        # ボタンフレーム
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(pady=20)

        # 更新ボタン
        ttk.Button(
            button_frame,
            text="パスワードを更新",
            command=self.update_password
        ).pack(pady=5)

        # 戻るボタン
        ttk.Button(
            button_frame,
            text="ログイン画面に戻る",
            command=self.back_to_login_callback
        ).pack(pady=5)

    def update_password(self):
        """パスワードの更新"""
        new_password = self.new_password.get()
        confirm_password = self.confirm_password.get()

        if not new_password or not confirm_password:
            messagebox.showwarning("警告", "パスワードを入力してください")
            return

        if new_password != confirm_password:
            messagebox.showerror("エラー", "パスワードが一致しません")
            return

        try:
            # パスワードの更新
            updates = {'password': new_password}
            self.user_model.update_user(self.verification_data['user_id'], updates)
            
            messagebox.showinfo("成功", "パスワードが更新されました")
            self.back_to_login_callback()

        except Exception as e:
            logger.error(f"Error updating password: {e}")
            messagebox.showerror("エラー", "パスワードの更新に失敗しました")

    def show(self):
        """画面の表示"""
        self.frame.tkraise()