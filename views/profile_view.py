import tkinter as tk
from tkinter import ttk, messagebox
from models.user import User
from models.post import Post
from models.follow import Follow
from models.like import Like
from models.comment import Comment
from views.follow_list_view import FollowListView
from views.comment_dialog import CommentDialog
from utils.notification import NotificationManager
from utils.email_sender import EmailSender  # 既存のEmailSenderクラスをインポート
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ProfileView:
    def __init__(self, parent, session_manager, app, user_id=None):
        """初期化"""
        try:
            # 基本的な属性の設定
            self.parent = parent
            self.session_manager = session_manager
            self.app = app
            self.user_id = user_id
            
            # モデルのインスタンス化
            self.user_model = User()
            self.post_model = Post()
            self.follow_model = Follow()
            self.like_model = Like()
            self.comment_model = Comment()
            
            
            # キャンバスとスクロール可能なフレームの参照を保持
            self.canvas = None
            self.scrollable_frame = None
            self.frame = None
            
            # 現在のユーザー情報を取得
            self.current_user = self.session_manager.get_current_user()
            if not self.current_user:
                raise ValueError("ユーザーがログインしていません")
            
            try:
                email_sender = EmailSender(
                    smtp_server=os.getenv('SMTP_SERVER'),
                    smtp_port=int(os.getenv('SMTP_PORT', 587)),
                    username=os.getenv('SMTP_USERNAME'),
                    password=os.getenv('SMTP_PASSWORD')
                )
                logger.debug(f"EmailSender initialized: {email_sender}")
                self.notification_manager = NotificationManager(email_sender)
                logger.debug("NotificationManager initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize email services: {e}", exc_info=True)
                self.notification_manager = None
                
            self.profile_user_id = user_id if user_id else self.current_user['user_id']
            self.profile_user = self.user_model.get_user(self.profile_user_id)
            
            # プロフィールユーザーの設定
            if self.user_id:
                self.profile_user = self.user_model.get_user(self.user_id)
                if not self.profile_user:
                    raise ValueError(f"ユーザーID {self.user_id} が見つかりません")
            else:
                self.profile_user = self.current_user
                self.user_id = self.current_user['user_id']

            # self.userの設定（互換性のため）
            self.user = self.profile_user

            print(f"Initialized ProfileView - Current user: {self.current_user['username']}, Profile user: {self.profile_user['username']}")

            # ウィジェットの作成
            self.create_widgets()

        except Exception as e:
            print(f"Error in ProfileView initialization: {e}")
            self.show_error_message(f"プロフィール画面の初期化に失敗しました: {e}")

    def create_widgets(self):
        # メインフレーム
        self.frame = ttk.Frame(self.parent, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # ナビゲーションバー
        self.create_navigation_bar()

        # プロフィール情報部分
        self.create_profile_info()

        # 投稿一覧
        self.create_posts_area()

    def create_post_widget(self, post):
        """投稿の表示ウィジェット作成（改良版）"""
        # 投稿全体のコンテナ
        post_container = ttk.Frame(self.scrollable_frame)
        post_container.pack(fill=tk.X, pady=5)

        # 上部の区切り線
        ttk.Separator(post_container, orient="horizontal").pack(fill=tk.X, pady=(0, 5))

        # 投稿本体のフレーム
        post_frame = ttk.Frame(post_container, style="Post.TFrame")
        post_frame.pack(fill=tk.X, padx=10)

        # 中央寄せのための内部フレーム
        inner_frame = ttk.Frame(post_frame)
        inner_frame.pack(anchor=tk.CENTER)

        # ヘッダー部分（ユーザー情報と時間）
        header_frame = ttk.Frame(inner_frame, style="PostHeader.TFrame")
        header_frame.pack(fill=tk.X, pady=5)

        # 投稿時間を右側に配置
        time_label = ttk.Label(
            header_frame,
            text=post['created_at'].strftime("%Y-%m-%d %H:%M"),
            font=('Helvetica', 9),
            foreground='gray'
        )
        time_label.pack(side=tk.RIGHT)

        # 投稿内容（中央寄せ）
        content_frame = ttk.Frame(inner_frame)
        content_frame.pack(fill=tk.X, pady=10)
        
        content_label = ttk.Label(
            content_frame,
            text=post['content'],
            wraplength=500,
            justify=tk.CENTER,
            font=('Helvetica', 10)
        )
        content_label.pack(expand=True)

        # アクションボタンフレーム（いいね、コメント）
        actions_frame = ttk.Frame(inner_frame)
        actions_frame.pack(fill=tk.X, pady=5)

        # いいねボタン
        like_count = self.like_model.get_like_count(post['post_id'])
        like_button = ttk.Button(
            actions_frame,
            text=f"❤ {like_count}",
            command=lambda: self.toggle_like(post),
            width=10
        )
        like_button.pack(side=tk.LEFT, padx=5)

        # コメントボタン
        comment_count = self.comment_model.get_comment_count(post['post_id'])
        comment_button = ttk.Button(
            actions_frame,
            text=f"💬 {comment_count}",
            command=lambda: self.show_comments(post['post_id']),
            width=12
        )
        comment_button.pack(side=tk.LEFT, padx=5)

        # 下部の区切り線
        ttk.Separator(post_container, orient="horizontal").pack(fill=tk.X, pady=(5, 0))

    def create_header(self):
        """ヘッダー部分の作成"""
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # 戻るボタン
        back_button = ttk.Button(
            header_frame,
            text="← タイムラインに戻る",
            command=self.back_to_timeline
        )
        back_button.pack(side=tk.LEFT)

    def create_profile_info(self):
        """プロフィール情報とフォロー関連の表示"""
        try:
            profile_frame = ttk.Frame(self.frame)
            profile_frame.pack(fill=tk.X, pady=20)

            # ユーザー名表示
            username_label = ttk.Label(
                profile_frame,
                text=self.profile_user['username'],
                font=('Helvetica', 16, 'bold')
            )
            username_label.pack(anchor=tk.W)

            # フォロー情報フレーム
            follow_frame = ttk.Frame(profile_frame)
            follow_frame.pack(fill=tk.X, pady=10)

            # フォロー/フォロワー情報を取得
            followers = self.follow_model.get_followers(self.profile_user['user_id'])
            following = self.follow_model.get_following(self.profile_user['user_id'])

            # フォロー中ボタン（クリックで一覧表示）
            following_button = ttk.Button(
                follow_frame,
                text=f"フォロー中: {len(following) if following else 0}",
                command=lambda: self.show_following_list(following if following else [])
            )
            following_button.pack(side=tk.LEFT, padx=5)
            
            # フォロワーボタン（クリックで一覧表示）
            followers_button = ttk.Button(
                follow_frame,
                text=f"フォロワー: {len(followers) if followers else 0}",
                command=lambda: self.show_followers_list(followers if followers else [])
            )
            followers_button.pack(side=tk.LEFT, padx=5)


            # 他のユーザーのプロフィールの場合のみフォローボタンを表示
            if self.profile_user['user_id'] != self.current_user['user_id']:
                is_following = self.follow_model.is_following(
                    self.current_user['user_id'],
                    self.profile_user['user_id']
                )

                self.follow_button = ttk.Button(
                    follow_frame,
                    text="フォロー中" if is_following else "フォロー",
                    command=self.toggle_follow
                )
                self.follow_button.pack(side=tk.RIGHT, padx=5)

        except Exception as e:
            print(f"Error in create_profile_info: {e}")  # デバッグ出力追加
            messagebox.showerror("エラー", f"プロフィール情報の表示中にエラーが発生しました: {e}")

# ProfileViewクラス内のメソッドを修正

    def show_followers_list(self, followers):
        """フォロワー一覧ページへの遷移"""
        try:
            for widget in self.parent.winfo_children():
                widget.destroy()
            follow_list_view = FollowListView(self.parent, self.session_manager, self.app, self.profile_user['user_id'])
            follow_list_view.tab_control.select(1)  # フォロワータブを選択
            follow_list_view.show()
        except Exception as e:
            messagebox.showerror("エラー", f"フォロワー一覧の表示中にエラーが発生しました: {e}")

    def show_following_list(self, following):
        """フォロー中一覧ページへの遷移"""
        try:
            for widget in self.parent.winfo_children():
                widget.destroy()
            follow_list_view = FollowListView(self.parent, self.session_manager, self.app, self.profile_user['user_id'])
            follow_list_view.tab_control.select(0)  # フォロー中タブを選択
            follow_list_view.show()
        except Exception as e:
            messagebox.showerror("エラー", f"フォロー中一覧の表示中にエラーが発生しました: {e}")

    def toggle_follow(self):
        """フォロー状態の切り替え"""
        try:
            is_following = self.follow_model.is_following(
                self.current_user['user_id'],
                self.profile_user['user_id']
            )

            if is_following:
                # フォロー解除
                self.follow_model.unfollow_user(
                    self.current_user['user_id'],
                    self.profile_user['user_id']
                )
                self.follow_button.configure(text="フォロー")
            else:
                # フォロー
                self.follow_model.follow_user(
                    self.current_user['user_id'],
                    self.profile_user['user_id']
                )
                
                # フォロー時のメール通知
                if self.notification_manager:
                    try:
                        followed_user = self.user_model.get_user(self.profile_user['user_id'])
                        logger.debug(f"Sending follow notification to: {followed_user['email']}")
                        
                        self.notification_manager.notify_new_follower(
                            followed_user['email'],
                            self.current_user['username']
                        )
                        logger.debug("Follow notification email sent successfully")
                    except Exception as e:
                        logger.error(f"Failed to send follow notification: {e}", exc_info=True)
                        # メール送信の失敗は無視して続行
                else:
                    logger.warning("NotificationManager is not available, skipping email notification")
                
                self.follow_button.configure(text="フォロー中")

            # プロフィール情報を更新
            self.refresh_profile_info()
            print(f"Follow status toggled successfully. Is following: {not is_following}")

        except Exception as e:
            logger.error(f"Error in toggle_follow: {e}", exc_info=True)
            messagebox.showerror("エラー", f"フォロー状態の更新中にエラーが発生しました: {e}")

    def unfollow_and_refresh(self, user_id):
        """フォロー解除してリストを更新"""
        try:
            self.follow_model.unfollow_user(
                self.current_user['user_id'],
                user_id
            )
            self.refresh_profile_info()
            messagebox.showinfo("成功", "フォローを解除しました")
        except Exception as e:
            messagebox.showerror("エラー", f"フォロー解除中にエラーが発生しました: {e}")

    def show_user_profile(self, user_id):
        """ユーザープロフィールページに遷移"""
        try:
            self.__init__(self.parent, self.session_manager, self.app, user_id)
        except Exception as e:
            messagebox.showerror("エラー", f"プロフィール表示中にエラーが発生しました: {e}")

    def create_posts_area(self):
        """投稿一覧エリアの作成（エラー修正版）"""
        posts_frame = ttk.LabelFrame(self.frame, text="投稿一覧", padding="10")
        posts_frame.pack(fill=tk.BOTH, expand=True)

        # スクロール可能な領域
        self.canvas = tk.Canvas(posts_frame)
        scrollbar = ttk.Scrollbar(posts_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # スクロールバーの設定
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # マウスホイールでのスクロールを有効化
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # マウスホイールイベントのバインド
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # キャンバスが非表示になった時にマウスホイールバインドを解除
        def _unbind_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        self.canvas.bind("<Unmap>", _unbind_mousewheel)

        # スクロール領域の設定
        def _configure_frame(event):
            # キャンバスのスクロール範囲を設定
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.scrollable_frame.bind("<Configure>", _configure_frame)
        
        # キャンバス内に投稿フレームを配置
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # キャンバスのサイズ変更時の処理
        def _on_canvas_configure(event):
            # 投稿フレームの幅をキャンバスの幅に合わせる
            self.canvas.itemconfig(
                self.canvas.find_withtag("all")[0],
                width=event.width
            )
        self.canvas.bind("<Configure>", _on_canvas_configure)

        # レイアウト
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 投稿の読み込み
        self.load_user_posts()

    def load_user_posts(self):
        """ユーザーの投稿を読み込んで表示"""
        try:
            posts = self.post_model.get_user_posts(self.user['user_id'])
            if not posts:
                ttk.Label(
                    self.scrollable_frame,
                    text="投稿がありません。",
                    font=('Helvetica', 10)
                ).pack(pady=10)
            else:
                for post in posts:
                    self.create_post_widget(post)
        except Exception as e:
            messagebox.showerror("エラー", f"投稿の読み込み中にエラーが発生しました: {e}")
            
    def load_user_profile(self):
        """ユーザー情報の再読み込み"""
        try:
            # ユーザー情報を再取得
            if self.user_id:
                self.profile_user = self.user_model.get_user(self.user_id)
            else:
                self.profile_user = self.current_user

            # UIの再構築
            self.create_navigation_bar()
            self.create_profile_info()
            self.create_posts_area()

            print(f"User profile loaded: {self.profile_user['username']}")  # デバッグ出力

        except Exception as e:
            print(f"Error in load_user_profile: {e}")  # デバッグ出力
            messagebox.showerror("エラー", f"ユーザー情報の再読み込み中にエラーが発生しました: {e}")

    def back_to_timeline(self):
        """タイムラインに戻る"""
        for widget in self.parent.winfo_children():
            widget.destroy()
        from views.timeline_view import TimelineView
        timeline_view = TimelineView(self.parent, self.session_manager, self.app)
        timeline_view.show()

    def user_is_current_user(self):
        """現在のユーザーと表示するユーザーが同じか確認"""
        current_user = self.session_manager.get_current_user()
        return current_user['user_id'] == self.user['user_id']

    def follow_user(self):
        """ユーザーをフォローする"""
        try:
            current_user = self.session_manager.get_current_user()
            self.follow_model.follow_user(current_user['user_id'], self.user['user_id'])
            messagebox.showinfo("成功", "ユーザーをフォローしました。")
        except Exception as e:
            messagebox.showerror("エラー", f"フォロー中にエラーが発生しました: {e}")

    def show_following(self):
        """フォロー中一覧の表示"""
        FollowListView(self.parent, self.session_manager, self.user['user_id'], "following")

    def show_followers(self):
        """フォロワー一覧の表示"""
        FollowListView(self.parent, self.session_manager, self.user['user_id'], "followers")

    def search_hashtag(self, hashtag):
        """ハッシュタグ検索"""
        try:
            for widget in self.parent.winfo_children():
                widget.destroy()
            from views.search_view import SearchView
            search_view = SearchView(self.parent, self.session_manager, self.app)
            search_view.search_type.set("hashtag")
            search_view.search_entry.insert(0, hashtag)
            search_view.search()
            search_view.show()
        except Exception as e:
            messagebox.showerror("エラー", f"検索中にエラーが発生しました: {e}")

    def show_user_profile(self, user_id):
        """他のユーザーのプロフィール画面の表示"""
        try:
            for widget in self.parent.winfo_children():
                widget.destroy()
            profile_view = ProfileView(self.parent, self.session_manager, self.app, user_id=user_id)
            profile_view.show()
        except Exception as e:
            messagebox.showerror("エラー", f"ユーザーのプロフィール画面の表示中にエラーが発生しました: {e}")

    def toggle_like(self, post):
        """いいねの切り替え"""
        try:
            user = self.session_manager.get_current_user()
            if self.like_model.toggle_like(user['user_id'], post['post_id']):
                messagebox.showinfo("成功", "いいねしました！")
            else:
                messagebox.showinfo("成功", "いいねを取り消しました！")
            self.refresh_posts()
        except Exception as e:
            messagebox.showerror("エラー", f"いいねの処理中にエラーが発生しました: {e}")

    def show_comments(self, post_id):
        """コメントダイアログの表示"""
        try:
            comment_dialog = CommentDialog(
                self.parent, 
                post_id, 
                self.session_manager,
                refresh_callback=self.refresh_posts  # 更新用のコールバックを渡す
            )
            comment_dialog.grab_set()  # モーダルダイアログとして表示
        except Exception as e:
            messagebox.showerror("エラー", f"コメントダイアログの表示中にエラーが発生しました: {e}")

    def refresh_posts(self):
        """投稿の更新"""
        # 投稿フレームをクリアして再作成
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.load_user_posts()
    
    def refresh_profile_info(self):
        """プロフィール情報の更新"""
        try:
            # プロフィール情報フレームをクリア
            for widget in self.frame.winfo_children():
                widget.destroy()

            # ユーザー情報とUIを再読み込み
            self.load_user_profile()

            print(f"Profile refreshed for user: {self.profile_user['username']}")  # デバッグ出力

        except Exception as e:
            print(f"Error in refresh_profile_info: {e}")  # デバッグ出力
            messagebox.showerror("エラー", "プロフィール情報の更新に失敗しました")
    
    
    def show(self):
        """画面を表示"""
        try:
            self.frame.tkraise()
        except Exception as e:
            print(f"Error in show method: {e}")
            self.show_error_message("画面の表示に失敗しました")
            
    def show_error_message(self, message):
        """エラーメッセージを表示"""
        try:
            if not hasattr(self, 'frame'):
                self.frame = ttk.Frame(self.parent, padding="20")
                self.frame.pack(fill=tk.BOTH, expand=True)
            
            error_label = ttk.Label(
                self.frame,
                text=message,
                foreground="red"
            )
            error_label.pack(pady=20)
        except Exception as e:
            print(f"Error showing error message: {e}")
            messagebox.showerror("エラー", message)
            
    def create_navigation_bar(self):
        """ナビゲーションバーの作成"""
        nav_frame = ttk.Frame(self.frame)
        nav_frame.pack(fill=tk.X, pady=(0, 20))

        # タイムラインボタン
        timeline_button = ttk.Button(
            nav_frame,
            text="🏠 タイムライン",
            command=self.show_timeline
        )
        timeline_button.pack(side=tk.LEFT, padx=5)

        # 検索ボタン
        search_button = ttk.Button(
            nav_frame,
            text="🔍 検索",
            command=self.show_search
        )
        search_button.pack(side=tk.LEFT, padx=5)

        # プロフィールボタン
        profile_button = ttk.Button(
            nav_frame,
            text="👤 プロフィール",
            command=self.show_own_profile  # メソッド名を変更
        )
        profile_button.pack(side=tk.LEFT, padx=5)

        # 設定ボタン
        settings_button = ttk.Button(
            nav_frame,
            text="⚙️ 設定",
            command=self.show_settings
        )
        settings_button.pack(side=tk.LEFT, padx=5)

        # ログアウトボタン
        logout_button = ttk.Button(
            nav_frame,
            text="🚪 ログアウト",
            command=self.logout
        )
        logout_button.pack(side=tk.RIGHT, padx=5)

    def show_timeline(self):
        """タイムライン画面への遷移"""
        try:
            for widget in self.parent.winfo_children():
                widget.destroy()
            from views.timeline_view import TimelineView
            timeline_view = TimelineView(self.parent, self.session_manager, self.app)
            timeline_view.show()
        except Exception as e:
            messagebox.showerror("エラー", f"タイムライン画面の表示中にエラーが発生しました: {e}")

    def show_own_profile(self):
        """自分のプロフィール画面への遷移"""
        try:
            if not self.user_is_current_user():
                for widget in self.parent.winfo_children():
                    widget.destroy()
                profile_view = ProfileView(
                    self.parent,
                    self.session_manager,
                    self.app,
                    user_id=None  # 自分のプロフィールを表示
                )
                profile_view.show()
        except Exception as e:
            messagebox.showerror("エラー", f"プロフィール画面の表示中にエラーが発生しました: {e}")

    def show_search(self):
        """検索画面への遷移"""
        try:
            for widget in self.parent.winfo_children():
                widget.destroy()
            from views.search_view import SearchView
            search_view = SearchView(self.parent, self.session_manager, self.app)
            search_view.show()
        except Exception as e:
            messagebox.showerror("エラー", f"検索画面の表示中にエラーが発生しました: {e}")

    def show_settings(self):
        """設定画面への遷移"""
        try:
            for widget in self.parent.winfo_children():
                widget.destroy()
            from views.settings_view import SettingsView
            settings_view = SettingsView(self.parent, self.session_manager, self.app)
            settings_view.show()
        except Exception as e:
            messagebox.showerror("エラー", f"設定画面の表示中にエラーが発生しました: {e}")

    def logout(self):
        """ログアウト処理"""
        try:
            if messagebox.askyesno("確認", "ログアウトしますか？"):
                self.session_manager.logout()
                self.app.show_login()
        except Exception as e:
            messagebox.showerror("エラー", f"ログアウト中にエラーが発生しました: {e}")

    def follow(self):
        """フォロー処理"""
        try:
            # フォロー関係を作成
            self.follow_model.create_follow(
                self.current_user['user_id'],
                self.profile_user_id
            )
            
            # メール通知の送信（通知マネージャーが利用可能な場合のみ）
            if self.notification_manager:
                try:
                    followed_user = self.user_model.get_user(self.profile_user_id)
                    self.notification_manager.notify_new_follower(
                        followed_user['email'],
                        self.current_user['username']
                    )
                except Exception as e:
                    logger.error(f"Failed to send follow notification email: {e}")
                    # メール送信の失敗は無視して続行
            
            # フォローボタンを解除ボタンに変更
            self.follow_button.configure(
                text="フォロー解除",
                command=self.unfollow
            )
            
            # フォロワー数を更新
            self.update_follower_count()
            
            messagebox.showinfo(
                "成功",
                f"{self.profile_user['username']}さんをフォローしました。"
            )
            
        except Exception as e:
            messagebox.showerror(
                "エラー",
                f"フォローに失敗しました：\n{str(e)}"
            )