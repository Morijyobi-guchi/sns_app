import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from models.user import User
from datetime import datetime, timedelta
import logging
import secrets
import string
from utils.email_sender import EmailSender
import os

logger = logging.getLogger(__name__)

class SettingsView:
    def __init__(self, parent, session_manager, app):
        try:
            self.parent = parent
            self.session_manager = session_manager
            self.app = app
            self.user_model = User()
            self.current_user = self.session_manager.get_current_user()
            
            # メール送信機能の初期化
            try:
                from utils.email_sender import EmailSender
                self.email_sender = EmailSender(
                    smtp_server=os.getenv('SMTP_SERVER'),
                    smtp_port=int(os.getenv('SMTP_PORT', 587)),
                    username=os.getenv('SMTP_USERNAME'),
                    password=os.getenv('SMTP_PASSWORD')
                )
                logger.info("Email sender initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize email sender: {e}")
                self.email_sender = None
                messagebox.showerror(
                    "エラー",
                    "メール送信機能の初期化に失敗しました。\n"
                    f"エラー: {str(e)}"
                )

            # ユーザー情報の取得
            try:
                self.user_details = self.user_model.get_user(self.current_user['user_id'])
                if not self.user_details:
                    raise Exception("ユーザー情報が取得できません")
            except Exception as e:
                logger.error(f"Failed to get user details: {e}")
                raise

            # メインフレーム
            self.frame = ttk.Frame(self.parent, padding="20")
            self.frame.pack(fill=tk.BOTH, expand=True)

            self.create_widgets()

        except Exception as e:
            logger.error(f"SettingsView initialization error: {e}")
            messagebox.showerror("エラー", f"設定画面の初期化に失敗しました: {str(e)}")
            raise

    def create_widgets(self):
        """ウィジェットの作成"""
        try:
            # 既存のウィジェットをクリア
            for widget in self.frame.winfo_children():
                widget.destroy()

            # ナビゲーションバー
            self.create_navigation_bar()

            # メール設定セクション
            self.create_email_section()

            # その他の設定フォーム
            self.create_settings_form()

        except Exception as e:
            logger.error(f"ウィジェット作成エラー: {e}")
            messagebox.showerror("エラー", "画面の作成に失敗しました")

    def create_navigation_bar(self):
        """ナビゲーションバーの作成"""
        try:
            nav_frame = ttk.Frame(self.frame)
            nav_frame.pack(fill=tk.X, pady=(0, 20))

            # タイムラインボタン
            ttk.Button(
                nav_frame,
                text="🏠 タイムライン",
                command=self.show_timeline
            ).pack(side=tk.LEFT, padx=5)

            # 検索ボタン
            ttk.Button(
                nav_frame,
                text="🔍 検索",
                command=self.show_search
            ).pack(side=tk.LEFT, padx=5)

            # プロフィールボタン
            ttk.Button(
                nav_frame,
                text="👤 プロフィール",
                command=self.show_profile
            ).pack(side=tk.LEFT, padx=5)

            # 設定ボタン
            ttk.Button(
                nav_frame,
                text="⚙️ 設定",
                command=self.show_settings
            ).pack(side=tk.LEFT, padx=5)

            # ログアウトボタン
            ttk.Button(
                nav_frame,
                text="🚪 ログアウト",
                command=self.logout
            ).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            logger.error(f"Error creating navigation bar: {e}")
            raise
        
    def create_settings_form(self):
        """設定フォームの作成"""
        # フォームフレーム
        form_frame = ttk.LabelFrame(self.frame, text="アカウント設定", padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)

        # ユーザー名設定
        username_frame = ttk.Frame(form_frame)
        username_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(username_frame, text="ユーザー名:").pack(side=tk.LEFT)
        self.username_entry = ttk.Entry(username_frame, width=30)
        self.username_entry.insert(0, self.current_user['username'])
        self.username_entry.pack(side=tk.LEFT, padx=10)

        # ユーザー名更新ボタン
        username_button = ttk.Button(
            username_frame,
            text="ユーザー名を更新",
            command=self.update_username,
            width=15
        )
        username_button.pack(side=tk.LEFT, padx=5)

        # メールアドレス表示（読み取り専用）
        email_frame = ttk.Frame(form_frame)
        email_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(email_frame, text="メールアドレス:").pack(side=tk.LEFT)
        email_label = ttk.Label(
            email_frame,
            text=self.user_details['email'],
            foreground="gray"
        )
        email_label.pack(side=tk.LEFT, padx=10)

        # パスワード変更
        password_frame = ttk.Frame(form_frame)
        password_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(password_frame, text="新しいパスワード:").pack(side=tk.LEFT)
        self.password_entry = ttk.Entry(password_frame, show="*", width=30)
        self.password_entry.pack(side=tk.LEFT, padx=10)

        # パスワード確認
        confirm_frame = ttk.Frame(form_frame)
        confirm_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(confirm_frame, text="パスワード確認:").pack(side=tk.LEFT)
        self.confirm_entry = ttk.Entry(confirm_frame, show="*", width=30)
        self.confirm_entry.pack(side=tk.LEFT, padx=10)

        # パスワード更新ボタン
        password_button = ttk.Button(
            confirm_frame,
            text="パスワードを更新",
            command=self.update_password,
            width=15
        )
        password_button.pack(side=tk.LEFT, padx=5)

        # 危険な操作セクション
        danger_frame = ttk.LabelFrame(form_frame, text="危険な操作", padding="20")
        danger_frame.pack(fill=tk.X, pady=(20, 0))

        # 警告ラベル
        warning_label = ttk.Label(
            danger_frame,
            text="※アカウントを削除すると、すべてのデータが完全に削除され、復元できません。",
            foreground="red"
        )
        warning_label.pack(side=tk.LEFT, pady=10)

        # アカウント削除ボタン
        delete_button = ttk.Button(
            danger_frame,
            text="アカウントを削除",
            command=self.delete_account,
            style="Danger.TButton"
        )
        delete_button.pack(side=tk.RIGHT, pady=10)

    def update_settings(self):
        """設定の更新処理"""
        try:
            updates = {}
            new_username = self.username_entry.get().strip()
            new_email = self.email_entry.get().strip()
            new_password = self.password_entry.get()
            confirm_password = self.confirm_entry.get()

            # ユーザー名の検証
            if new_username != self.current_user['username']:
                if not new_username:
                    messagebox.showerror("エラー", "ユーザー名は必須です。")
                    return
                updates['username'] = new_username

            # メールアドレスの検証
            if new_email != self.current_user['email']:
                if not new_email:
                    messagebox.showerror("エラー", "メールアドレスは必須です。")
                    return
                updates['email'] = new_email

            # パスワードの検証
            if new_password:
                if new_password != confirm_password:
                    messagebox.showerror("エラー", "パスワードが一致しません。")
                    return
                updates['password'] = new_password

            if updates:
                # 更新実行
                self.user_model.update_user(self.current_user['user_id'], updates)
                messagebox.showinfo("成功", "設定を更新しました。")
                
                # セッション情報も更新
                updated_user = self.user_model.get_user(self.current_user['user_id'])
                self.session_manager.set_current_user(updated_user)
                
                # パスワードフィールドをクリア
                self.password_entry.delete(0, tk.END)
                self.confirm_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("エラー", f"設定の更新中にエラーが発生しました: {e}")

    def show_timeline(self):
        """タイムライン画面への遷移"""
        for widget in self.parent.winfo_children():
            widget.destroy()
        from views.timeline_view import TimelineView
        timeline_view = TimelineView(self.parent, self.session_manager, self.app)
        timeline_view.show()

    def show_search(self):
        """検索画面への遷移"""
        for widget in self.parent.winfo_children():
            widget.destroy()
        from views.search_view import SearchView
        search_view = SearchView(self.parent, self.session_manager, self.app)
        search_view.show()

    def show_profile(self):
        """プロフィール画面への遷移"""
        for widget in self.parent.winfo_children():
            widget.destroy()
        from views.profile_view import ProfileView
        profile_view = ProfileView(self.parent, self.session_manager, self.app)
        profile_view.show()

    def show_settings(self):
        """設定画面の再表示"""
        self.frame.tkraise()

    def logout(self):
        """ログアウト処理"""
        if messagebox.askyesno("確認", "ログアウトしますか？"):
            self.session_manager.logout()
            self.app.show_login()

    def show(self):
        """画面の表示"""
        try:
            if not hasattr(self, 'frame'):
                self.frame = ttk.Frame(self.parent, padding="20")
                self.frame.pack(fill=tk.BOTH, expand=True)
                self.create_widgets()
            self.frame.tkraise()
        except Exception as e:
            logger.error(f"Error showing settings view: {e}")
            messagebox.showerror("エラー", "設定画面の表示に失敗しました")
        

    def delete_account(self):
        """アカウント削除処理"""
        # 確認ダイアログを表示
        if not messagebox.askyesno(
            "確認",
            "本当にアカウントを削除しますか？\n"
            "この操作は取り消せず、すべてのデータが完全に削除されます。\n"
            "• 投稿\n"
            "• コメント\n"
            "• いいね\n"
            "• フォロー/フォロワー\n"
            "などのすべての情報が失われます。"
        ):
            return

        # パスワード確認ダイアログ
        password = simpledialog.askstring(
            "確認",
            "セキュリティのため、現在のパスワードを入力してください：",
            show="*"
        )
        
        if not password:
            return

        try:
            # パスワードの検証
            if not self.user_model.verify_password(
                self.current_user['user_id'],
                password
            ):
                messagebox.showerror(
                    "エラー",
                    "パスワードが正しくありません。"
                )
                return

            # アカウント削除の実行
            self.user_model.delete_user(self.current_user['user_id'])
            
            messagebox.showinfo(
                "完了",
                "アカウントが完全に削除されました。\n"
                "ご利用ありがとうございました。"
            )
            
            # セッションをクリアしてログイン画面に戻る
            self.session_manager.logout()
            self.app.show_login()

        except Exception as e:
            messagebox.showerror(
                "エラー",
                f"アカウントの削除中にエラーが発生しました：\n{str(e)}"
            )

    def update_username(self):
        """ユーザー名の更新処理"""
        new_username = self.username_entry.get().strip()
        
        if not new_username:
            messagebox.showerror("エラー", "ユーザー名は必須です。")
            return
            
        if new_username == self.current_user['username']:
            messagebox.showinfo("情報", "現在のユーザー名と同じです。")
            return
            
        try:
            # ユーザー名の更新を実行
            self.user_model.update_user(
                self.current_user['user_id'],
                {'username': new_username}
            )
            
            # セッション情報のユーザー名を更新
            self.session_manager.update_current_user(new_username)
            
            # 現在のユーザー情報を更新（ビューの表示用）
            self.current_user = self.session_manager.get_current_user()
            
            messagebox.showinfo(
                "成功",
                f"ユーザー名を「{new_username}」に更新しました。"
            )
            
        except Exception as e:
            if "このユーザー名は既に使用されています" in str(e):
                messagebox.showerror(
                    "エラー",
                    "このユーザー名は既に使用されています。"
                )
            else:
                messagebox.showerror(
                    "エラー",
                    f"ユーザー名の更新中にエラーが発生しました：\n{str(e)}"
                )

    def update_password(self):
        """パスワードの更新処理"""
        new_password = self.password_entry.get()
        confirm_password = self.confirm_entry.get()

        if not new_password:
            messagebox.showerror("エラー", "新しいパスワードを入力してください。")
            return

        if new_password != confirm_password:
            messagebox.showerror("エラー", "パスワードが一致しません。")
            return

        try:
            # パスワードの更新
            self.user_model.update_user(
                self.current_user['user_id'],
                {'password': new_password}
            )
            
            # パスワードフィールドをクリア
            self.password_entry.delete(0, tk.END)
            self.confirm_entry.delete(0, tk.END)
            
            messagebox.showinfo(
                "成功",
                "パスワードを更新しました。"
            )
            
        except Exception as e:
            messagebox.showerror(
                "エラー",
                f"パスワードの更新中にエラーが発生しました：\n{str(e)}"
            )

    def create_email_verification_view(self):
        """メール認証画面の作成"""
        try:
            # 既存のウィジェットをクリア
            for widget in self.frame.winfo_children():
                widget.destroy()

            # 認証フレーム
            verification_frame = ttk.Frame(self.frame, padding="20")
            verification_frame.pack(fill=tk.BOTH, expand=True)

            # タイトル
            ttk.Label(
                verification_frame,
                text="メールアドレス認証",
                font=('Helvetica', 14, 'bold')
            ).pack(pady=20)

            # 説明文
            ttk.Label(
                verification_frame,
                text="メールに送信された認証コードを入力してください。\n"
                     "有効期限は24時間です。",
                justify=tk.CENTER,
                wraplength=400
            ).pack(pady=10)

            # 認証コード入力
            code_frame = ttk.Frame(verification_frame)
            code_frame.pack(pady=20)

            ttk.Label(code_frame, text="認証コード:").pack(side=tk.LEFT, padx=5)
            self.code_entry = ttk.Entry(code_frame, width=40)
            self.code_entry.pack(side=tk.LEFT, padx=5)
            self.code_entry.focus()

            # ボタンフレーム
            button_frame = ttk.Frame(verification_frame)
            button_frame.pack(pady=20)

            # 認証ボタン
            ttk.Button(
                button_frame,
                text="認証する",
                command=self.verify_code
            ).pack(side=tk.LEFT, padx=5)

            # 戻るボタン
            ttk.Button(
                button_frame,
                text="戻る",
                command=self.create_widgets
            ).pack(side=tk.LEFT, padx=5)

        except Exception as e:
            logger.error(f"認証画面作成エラー: {e}")
            messagebox.showerror("エラー", "認証画面の作成に失敗しました")
            self.create_widgets()

    def create_other_settings(self):
        """その他の設定セクション"""
        # 必要に応じて他の設定を追加
        pass

    def show(self):
        """画面の表示"""
        self.frame.tkraise()


    def start_email_verification(self):
        """メール認証プロセスを開始"""
        try:
            logger.debug("Starting email verification process...")
            current_time = datetime.utcnow()
            
            # メール送信機能の確認
            if not hasattr(self, 'email_sender') or not self.email_sender:
                logger.error("Email sender is not initialized")
                messagebox.showerror(
                    "エラー",
                    "メール送信機能が初期化されていません。\n"
                    "アプリケーションを再起動してください。"
                )
                return

            # ユーザー情報の確認
            if not hasattr(self, 'user_details') or not self.user_details:
                logger.error(f"User details not found for user: {self.current_user['username']}")
                messagebox.showerror(
                    "エラー", 
                    "ユーザー情報が取得できません。\n"
                    "画面を更新してください。"
                )
                return

            logger.info(f"Starting verification for user: {self.user_details['username']}")
            logger.debug(f"User email: {self.user_details['email']}")
            logger.debug(f"Current UTC time: {current_time}")

            # 認証コードの生成
            verification_code = ''.join(
                secrets.choice(string.ascii_letters + string.digits)
                for _ in range(32)
            )
            
            # 有効期限の設定（24時間）
            expiration = current_time + timedelta(hours=24)
            logger.debug(f"Code expiration time: {expiration}")

            # データベースに認証情報を保存
            try:
                logger.debug("Saving verification code to database...")
                self.user_model.set_verification_code(
                    self.user_details['user_id'],
                    verification_code,
                    expiration
                )
                logger.info("Verification code saved successfully")

            except Exception as e:
                logger.error(f"Database error while saving verification code: {e}")
                messagebox.showerror(
                    "エラー",
                    "認証コードの保存に失敗しました。\n"
                    "しばらく待ってから再度お試しください。"
                )
                return

            # メール送信
            try:
                logger.debug(f"Sending verification email to: {self.user_details['email']}")
                self.email_sender.send_verification_email(
                    self.user_details['email'],
                    verification_code
                )
                logger.info("Verification email sent successfully")

                messagebox.showinfo(
                    "送信完了",
                    "認証コードを記載したメールを送信しました。\n"
                    "メールをご確認ください。\n"
                    "※迷惑メールフォルダもご確認ください。"
                )
                
                # 認証画面に遷移
                self.create_email_verification_view()
                
            except Exception as e:
                logger.error(f"Error sending verification email: {e}")
                messagebox.showerror(
                    "エラー",
                    "メールの送信に失敗しました。\n"
                    "以下を確認してください：\n"
                    "・メールアドレスが正しいか\n"
                    "・インターネット接続が安定しているか\n"
                    f"\nエラー詳細: {str(e)}"
                )
                return

        except Exception as e:
            logger.error(f"Unexpected error in email verification process: {e}")
            messagebox.showerror(
                "エラー",
                "予期せぬエラーが発生しました。\n"
                "アプリケーションを再起動してください。\n"
                f"\nエラー詳細: {str(e)}"
            )

    def show_verification_dialog(self):
        """認証コード入力ダイアログ"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("メール認証")
        dialog.geometry("300x200")
        
        ttk.Label(
            dialog,
            text="メールに送信された認証コードを入力してください。\n(有効期限: 24時間)",
            wraplength=250
        ).pack(pady=10)
        
        code_entry = ttk.Entry(dialog, width=40)
        code_entry.pack(pady=10)
        
    def verify_code(self):
        """認証コードの検証"""
        try:
            code = self.code_entry.get().strip()
            if not code:
                messagebox.showwarning(
                    "警告",
                    "認証コードを入力してください。"
                )
                return

            logger.debug(f"Verifying code for user: {self.user_details['username']}")

            # 認証コードの検証
            try:
                if self.user_model.verify_email_code(self.user_details['user_id'], code):
                    # 認証成功時の処理
                    try:
                        self.user_model.update_email_verification_status(
                            self.user_details['user_id'],
                            True
                        )
                        
                        messagebox.showinfo(
                            "成功",
                            "メールアドレスが認証されました。"
                        )
                        
                        # 最新のユーザー情報を取得して画面を更新
                        self.user_details = self.user_model.get_user(
                            self.user_details['user_id']
                        )
                        self.create_widgets()
                        
                    except Exception as e:
                        logger.error(f"Error updating verification status: {e}")
                        messagebox.showerror(
                            "エラー",
                            "認証は成功しましたが、状態の更新に失敗しました。\n"
                            "もう一度お試しください。"
                        )
                else:
                    messagebox.showerror(
                        "エラー",
                        "認証コードが正しくないか、期限切れです。\n"
                        "コードを確認して再度お試しください。"
                    )
                    
            except Exception as e:
                logger.error(f"Error during code verification: {e}")
                raise

        except Exception as e:
            logger.error(f"Verification process error: {e}")
            messagebox.showerror(
                "エラー",
                "認証処理中にエラーが発生しました。\n"
                "しばらく待ってから再度お試しください。"
            )

    def refresh_view(self):
        """画面の更新"""
        try:
            # 最新のユーザー情報を取得
            self.user_details = self.user_model.get_user(self.user_details['user_id'])
            # 画面を再描画
            self.create_widgets()
        except Exception as e:
            logger.error(f"Error refreshing view: {e}")
            messagebox.showerror("エラー", "画面の更新に失敗しました")

    def create_email_section(self):
        """メール設定セクションの作成"""
        try:
            # メールフレームの作成
            email_frame = ttk.LabelFrame(self.frame, text="メール設定", padding="10")
            email_frame.pack(fill=tk.X, pady=10, padx=20)

            # メールアドレス表示
            current_email = self.user_details.get('email', '未設定')
            email_label = ttk.Label(
                email_frame,
                text=f"現在のメールアドレス: {current_email}"
            )
            email_label.pack(anchor=tk.W)

            # 認証状態の表示
            is_verified = self.user_details.get('is_email_verified', False)
            if is_verified:
                status_label = ttk.Label(
                    email_frame,
                    text="✓ 認証済み",
                    foreground="green"
                )
            else:
                status_label = ttk.Label(
                    email_frame,
                    text="⚠ 未認証",
                    foreground="red"
                )
            status_label.pack(anchor=tk.W)

            # 未認証の場合は認証ボタンを表示
            if not is_verified:
                verify_button = ttk.Button(
                    email_frame,
                    text="メールアドレスを認証する",
                    command=self.start_email_verification
                )
                verify_button.pack(pady=5)

        except Exception as e:
            logger.error(f"メール設定セクション作成エラー: {e}")
            raise