import tkinter as tk
from tkinter import ttk, messagebox
from models.post import Post
from models.user import User

class SearchView:
    def __init__(self, parent, session_manager, app):
        self.parent = parent
        self.session_manager = session_manager
        self.app = app
        self.post_model = Post()
        self.user_model = User()
        
        self.create_widgets()

    def create_widgets(self):
        # メインフレーム
        self.frame = ttk.Frame(self.parent, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # 検索タイプの選択
        self.search_type = tk.StringVar(value="user")
        
        # ラジオボタンフレーム
        radio_frame = ttk.LabelFrame(self.frame, text="検索タイプ", padding="10")
        radio_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Radiobutton(
            radio_frame,
            text="ユーザー検索",
            variable=self.search_type,
            value="user"
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Radiobutton(
            radio_frame,
            text="ハッシュタグ検索",
            variable=self.search_type,
            value="hashtag"
        ).pack(side=tk.LEFT, padx=10)

        # 検索フレーム
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill=tk.X, pady=(0, 20))

        # 検索入力
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # 検索ボタン
        search_button = ttk.Button(
            search_frame,
            text="検索",
            command=self.search
        )
        search_button.pack(side=tk.RIGHT)

        # 結果表示エリア
        self.result_frame = ttk.LabelFrame(self.frame, text="検索結果", padding="10")
        self.result_frame.pack(fill=tk.BOTH, expand=True)

        # 戻るボタン
        back_button = ttk.Button(
            self.frame,
            text="戻る",
            command=self.back_to_timeline
        )
        back_button.pack(pady=(20, 0))

    def search(self):
        # 検索結果をクリア
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("警告", "検索キーワードを入力してください。")
            return

        try:
            if self.search_type.get() == "user":
                self.search_users(query)
            else:
                self.search_hashtags(query)
        except Exception as e:
            messagebox.showerror("エラー", f"検索中にエラーが発生しました: {e}")

    def search_users(self, query):
        results = self.user_model.search_users(query)
        if not results:
            ttk.Label(
                self.result_frame,
                text="ユーザーが見つかりませんでした。"
            ).pack(pady=10)
            return

        for user in results:
            user_frame = ttk.Frame(self.result_frame)
            user_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(
                user_frame,
                text=user['username'],
                font=('Helvetica', 11, 'bold')
            ).pack(side=tk.LEFT)
            
            ttk.Button(
                user_frame,
                text="プロフィールを見る",
                command=lambda u=user: self.show_user_profile(u['user_id'])
            ).pack(side=tk.RIGHT)

    def search_hashtags(self, query):
        # #がない場合は自動的に追加
        if not query.startswith('#'):
            query = f"#{query}"
            
        results = self.post_model.search_posts_by_hashtag(query)
        if not results:
            ttk.Label(
                self.result_frame,
                text="投稿が見つかりませんでした。"
            ).pack(pady=10)
            return

        for post in results:
            self.create_post_widget(post)
            
    def create_post_widget(self, post):
        """ハッシュタグ検索結果の投稿表示（改良版）"""
        post_frame = ttk.Frame(self.result_frame, style="Post.TFrame")
        post_frame.pack(fill=tk.X, pady=5, padx=20)

        # ヘッダー（ユーザー名と時間）
        header_frame = ttk.Frame(post_frame)
        header_frame.pack(fill=tk.X, pady=5)

        username_label = ttk.Label(
            header_frame,
            text=post['username'],
            font=('Helvetica', 11, 'bold'),
            cursor="hand2"
        )
        username_label.pack(side=tk.LEFT)
        username_label.bind(
            "<Button-1>",
            lambda e, user_id=post['user_id']: self.show_user_profile(user_id)
        )

        time_label = ttk.Label(
            header_frame,
            text=post['created_at'].strftime("%Y-%m-%d %H:%M"),
            font=('Helvetica', 9),
            foreground='gray'
        )
        time_label.pack(side=tk.RIGHT)

        # 投稿内容（ハッシュタグを青色でクリッカブルに）
        content_frame = ttk.Frame(post_frame)
        content_frame.pack(fill=tk.X, pady=5)

        words = post['content'].split()
        for word in words:
            if word.startswith('#'):
                # ハッシュタグの場合
                label = ttk.Label(
                    content_frame,
                    text=word + " ",
                    font=('Helvetica', 10),
                    foreground='blue',
                    cursor="hand2"
                )
                label.pack(side=tk.LEFT)
                # 同じハッシュタグでの再検索が可能に
                label.bind(
                    "<Button-1>",
                    lambda e, tag=word: self.search_hashtags(tag)
                )
            else:
                # 通常のテキスト
                label = ttk.Label(
                    content_frame,
                    text=word + " ",
                    font=('Helvetica', 10)
                )
                label.pack(side=tk.LEFT)

        ttk.Separator(self.result_frame).pack(fill=tk.X, pady=5)

    def show_user_profile(self, user_id):
        """ユーザープロフィール表示（画面遷移版）"""
        try:
            # 現在の画面をクリア
            for widget in self.parent.winfo_children():
                widget.destroy()
            
            # プロフィール画面を表示
            from views.profile_view import ProfileView
            profile_view = ProfileView(
                parent=self.parent,
                session_manager=self.session_manager,
                app=self.app,  # appパラメータを渡す
                user_id=user_id
            )
            profile_view.show()
            
        except Exception as e:
            messagebox.showerror("エラー", f"プロフィール表示中にエラーが発生しました: {e}")

    def back_to_timeline(self):
        """タイムラインに戻る"""
        self.frame.destroy()
        self.app.show_timeline()

    def show(self):
        self.frame.tkraise()