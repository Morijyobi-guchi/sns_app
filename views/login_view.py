import tkinter as tk
from tkinter import ttk, messagebox
from models.user import User
import logging

logger = logging.getLogger(__name__)

class LoginView:
    def __init__(self, parent, session_manager, on_login_success, show_register_callback, show_password_reset_callback):
        self.parent = parent
        self.session_manager = session_manager
        self.on_login_success = on_login_success
        self.show_register_callback = show_register_callback
        self.show_password_reset_callback = show_password_reset_callback
        self.user_model = User()
        
        # メインフレームの作成
        self.frame = ttk.Frame(self.parent, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_widgets()

    def create_widgets(self):
        # タイトル
        title_label = ttk.Label(
            self.frame,
            text="ログイン",
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=20)
        
        # ユーザー名入力
        username_frame = ttk.Frame(self.frame)
        username_frame.pack(pady=5)
        
        ttk.Label(username_frame, text="ユーザー名:").pack(side=tk.LEFT)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(
            username_frame,
            textvariable=self.username_var
        )
        self.username_entry.pack(side=tk.LEFT, padx=5)
        
        # パスワード入力
        password_frame = ttk.Frame(self.frame)
        password_frame.pack(pady=5)
        
        ttk.Label(password_frame, text="パスワード:").pack(side=tk.LEFT)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(
            password_frame,
            textvariable=self.password_var,
            show="*"
        )
        self.password_entry.pack(side=tk.LEFT, padx=5)
        
        # ボタンフレーム
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(pady=20)
        
        # ログインボタン
        login_button = ttk.Button(
            button_frame,
            text="ログイン",
            command=self.on_login
        )
        login_button.pack(side=tk.LEFT, padx=5)
        
        # 新規登録ボタン
        register_button = ttk.Button(
            button_frame,
            text="新規登録",
            command=self.show_register_callback
        )
        register_button.pack(side=tk.LEFT, padx=5)

        # パスワードリセットリンク
        reset_link = ttk.Label(
            self.frame,
            text="パスワードを忘れた方はこちら",
            foreground="blue",
            cursor="hand2"
        )
        reset_link.pack(pady=10)
        reset_link.bind("<Button-1>", lambda e: self.show_password_reset_callback())

    def on_login(self):
        """ログイン処理"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("エラー", "ユーザー名とパスワードを入力してください。")
            return
        
        try:
            user_data = self.user_model.authenticate(username, password)
            if user_data:
                self.on_login_success(user_data)
            else:
                messagebox.showerror("エラー", "ユーザー名またはパスワードが正しくありません。")
        except Exception as e:
            messagebox.showerror("エラー", str(e))

    def show(self):
        """画面を表示"""
        self.frame.tkraise()