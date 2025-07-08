import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models.post import Post
from models.like import Like
from models.comment import Comment
from views.comment_dialog import CommentDialog
from views.profile_view import ProfileView
from models.user import User
from views.search_view import SearchView
import logging

class TimelineView:
    def __init__(self, parent, session_manager, app):
        self.parent = parent
        self.session_manager = session_manager
        self.post_model = Post()
        self.like_model = Like()
        self.user_model = User()
        self.comment_model = Comment()
        self.app = app
        self.current_user = self.session_manager.get_current_user()
        
        # スタイル設定
        self.style = ttk.Style()
        self.style.configure(
            "Post.TFrame",
            borderwidth=1
        )
        self.style.configure(
            "PostHeader.TFrame",
            padding=5
        )
        
        self.create_widgets()

    def create_widgets(self):
        # メインフレーム
        self.frame = ttk.Frame(self.parent, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # 左のナビゲーションバー
        self.create_navigation_bar()

        # ヘッダー部分（ユーザー情報）
        self.create_header()

        # 投稿フォーム
        self.create_post_form()

        # タイムライン表示エリア
        self.create_timeline_area()

        # 初期投稿の読み込み
        self.load_posts()

    def create_navigation_bar(self):
        nav_frame = ttk.Frame(self.frame, style="Nav.TFrame")
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        # ホームアイコン
        home_button = ttk.Button(nav_frame, text="🏠", command=self.show_timeline, width=3)
        home_button.pack(pady=(10, 20))

        # プロフィールアイコン
        profile_button = ttk.Button(nav_frame, text="👤", command=self.show_profile, width=3)
        profile_button.pack(pady=(10, 20))

        # 検索アイコン
        search_button = ttk.Button(nav_frame, text="🔍", command=self.show_search, width=3)
        search_button.pack(pady=(10, 20))

        # 設定アイコン（新規追加）
        settings_button = ttk.Button(nav_frame, text="⚙️", command=self.show_settings, width=3)
        settings_button.pack(pady=(10, 20))

    def create_header(self):
        """ヘッダー部分の作成（ユーザー情報とログアウトボタンを含む）"""
        # ヘッダーフレーム
        header_frame = ttk.Frame(self.frame, style="Header.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # 左側：現在時刻とユーザー情報
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.Y)

        # 現在時刻の表示
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        time_label = ttk.Label(
            info_frame,
            text=current_time,
            font=('Helvetica', 9),
            foreground='gray'
        )
        time_label.pack(anchor=tk.W)

        # ユーザー情報の表示
        user = self.session_manager.get_current_user()
        user_info = ttk.Label(
            info_frame,
            text=f"ログイン中: {user['username']}",
            font=('Helvetica', 12, 'bold')
        )
        user_info.pack(anchor=tk.W)

        # 右側：ログアウトボタン
        buttons_frame = ttk.Frame(header_frame)
        buttons_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # ログアウトボタン
        logout_btn = ttk.Button(
            buttons_frame,
            text="ログアウト",
            command=self.on_logout,
            style="Logout.TButton",
            width=12
        )
        logout_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # 区切り線
        separator = ttk.Separator(self.frame, orient="horizontal")
        separator.pack(fill=tk.X, pady=(5, 15))
        
    def create_post_form(self):
        """投稿フォームの作成（ハッシュタグ対応版）"""
        form_frame = ttk.LabelFrame(
            self.frame,
            padding="15",
            style="PostForm.TLabelframe"
        )
        form_frame.pack(fill=tk.X, pady=(0, 20))

        # 投稿入力エリア
        self.post_text = tk.Text(
            form_frame,
            height=4,
            font=('Helvetica', 11),
            wrap=tk.WORD
        )
        self.post_text.pack(fill=tk.X, pady=(5, 10))

        # ハッシュタグ用のタグを設定
        self.post_text.tag_configure(
            "hashtag",
            foreground="blue",
            font=('Helvetica', 11, 'bold')
        )

        # テキスト変更イベントをバインド
        self.post_text.bind('<KeyRelease>', self.highlight_hashtags)

        # ボタンフレーム
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X)

        # 投稿ボタン
        post_btn = ttk.Button(
            button_frame,
            text="投稿する",
            command=self.on_post,
            style="Post.TButton",
            width=15
        )
        post_btn.pack(side=tk.RIGHT)

    def create_timeline_area(self):
        """タイムライン表示エリアの作成（エラー修正版）"""
        # スクロール可能なタイムラインエリア
        timeline_frame = ttk.LabelFrame(self.frame, text="フォロー中", padding="10")
        timeline_frame.pack(fill=tk.BOTH, expand=True)

        # スクロール可能な領域
        self.canvas = tk.Canvas(timeline_frame)
        scrollbar = ttk.Scrollbar(timeline_frame, orient="vertical", command=self.canvas.yview)
        self.posts_frame = ttk.Frame(self.canvas)

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

        self.posts_frame.bind("<Configure>", _configure_frame)
        
        # キャンバス内に投稿フレームを配置
        self.canvas.create_window((0, 0), window=self.posts_frame, anchor="nw")

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
        self.load_posts()

    def load_posts(self):
        """投稿の読み込みと表示"""
        try:
            # 既存のウィジェットをクリア
            for widget in self.posts_frame.winfo_children():
                widget.destroy()

            # フォロー中と自分の投稿を取得
            posts = self.post_model.get_timeline_posts(self.current_user['user_id'])
            
            if not posts:
                no_posts_label = ttk.Label(
                    self.posts_frame,
                    text="まだ投稿がありません。\n新しい投稿を作成するか、ユーザーをフォローしてみましょう！",
                    font=('Helvetica', 10),
                    justify=tk.CENTER
                )
                no_posts_label.pack(pady=20)
                
                # ユーザー検索ボタンの追加
                search_button = ttk.Button(
                    self.posts_frame,
                    text="ユーザーを探す",
                    command=self.show_search_view
                )
                search_button.pack(pady=10)
            else:
                for post in posts:
                    self.create_post_widget(post)

        except Exception as e:
            logging.error(f"Error loading posts: {e}")
            messagebox.showerror("エラー", f"投稿の読み込み中にエラーが発生しました: {e}")

    def create_post_widget(self, post):
        """投稿の表示ウィジェットを作成（中央寄せ改良版）"""
        # 外側のコンテナ（中央寄せ用）
        outer_container = ttk.Frame(self.posts_frame)
        outer_container.pack(fill=tk.X, pady=5)
        
        # 中央寄せ用のフレーム
        centering_frame = ttk.Frame(outer_container)
        centering_frame.pack(pady=5)

        # 投稿コンテナ（固定幅で中央寄せ）
        post_container = ttk.Frame(centering_frame)
        post_container.pack(pady=5, padx=100)  # 左右のパディングで中央寄せ効果を作成
        
        # 投稿の最大幅を設定
        max_width = 600  # 投稿の最大幅を設定
        
        # 上部の区切り線
        ttk.Separator(post_container, orient="horizontal").pack(fill=tk.X)

        # 投稿本体のフレーム
        post_frame = ttk.Frame(post_container, style="Post.TFrame", width=max_width)
        post_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 投稿の内容が最大幅を超えないように設定
        post_frame.pack_propagate(False)
        post_frame.configure(height=150)  # 適切な高さを設定

        # ヘッダー部分（ユーザー情報と時間）
        header_frame = ttk.Frame(post_frame, style="PostHeader.TFrame")
        header_frame.pack(fill=tk.X, pady=5)

        # ユーザー名と時間の表示
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

        # 投稿内容フレーム
        content_frame = ttk.Frame(post_frame)
        content_frame.pack(fill=tk.X, pady=10)

        # 投稿内容を単語単位で分割して処理
        content = post['content']
        words = content.split()
        current_line_frame = ttk.Frame(content_frame)
        current_line_frame.pack(fill=tk.X)
        
        line_width = 0
        text_max_width = max_width - 40  # 左右のパディングを考慮

        for word in words:
            # 単語の推定幅
            word_width = len(word) * 7

            # 新しい行が必要かチェック
            if line_width + word_width > text_max_width:
                current_line_frame = ttk.Frame(content_frame)
                current_line_frame.pack(fill=tk.X)
                line_width = 0

            # ハッシュタグかどうかで分岐
            if word.startswith('#'):
                word_label = ttk.Label(
                    current_line_frame,
                    text=word,
                    font=('Helvetica', 10),
                    foreground='blue',
                    cursor="hand2"
                )
                word_label.bind(
                    "<Button-1>",
                    lambda e, tag=word: self.search_hashtag(tag)
                )
            else:
                word_label = ttk.Label(
                    current_line_frame,
                    text=word,
                    font=('Helvetica', 10)
                )
            
            word_label.pack(side=tk.LEFT, padx=(0, 3))
            line_width += word_width

        # アクションボタンフレーム
        actions_frame = ttk.Frame(post_frame)
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
        ttk.Separator(post_container, orient="horizontal").pack(fill=tk.X)
    
        

    def toggle_like(self, post):
        """いいねの切り替え"""
        try:
            user = self.session_manager.get_current_user()
            if self.like_model.toggle_like(user['user_id'], post['post_id']):
                messagebox.showinfo("成功", "いいねしました！")
            else:
                messagebox.showinfo("成功", "いいねを取り消しました！")
            self.refresh_timeline()
        except Exception as e:
            messagebox.showerror("エラー", f"いいねの処理中にエラーが発生しました: {e}")

    def show_comments(self, post_id):
        """コメントダイアログの表示"""
        try:
            comment_dialog = CommentDialog(
                self.parent, 
                post_id, 
                self.session_manager,
                refresh_callback=self.refresh_timeline  # タイムライン更新用のコールバックを渡す
            )
            comment_dialog.grab_set()  # モーダルダイアログとして表示
        except Exception as e:
            messagebox.showerror("エラー", f"コメントダイアログの表示中にエラーが発生しました: {e}")

    def refresh_timeline(self):
        """タイムラインの更新"""
        # 投稿フレームをクリアして再作成
        for widget in self.posts_frame.winfo_children():
            widget.destroy()
        self.load_posts()

    def on_post(self):
        """新規投稿の処理"""
        content = self.post_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "投稿内容を入力してください。")
            return

        try:
            user = self.session_manager.get_current_user()
            self.post_model.create_post(user['user_id'], content)

            # 投稿エリアをクリア
            self.post_text.delete("1.0", tk.END)

            # タイムラインを更新
            self.refresh_timeline()
            
            messagebox.showinfo("成功", "投稿しました！")

        except Exception as e:
            messagebox.showerror("エラー", f"投稿中にエラーが発生しました: {e}")

    def on_logout(self):
        """ログアウト処理"""
        if messagebox.askyesno("確認", "ログアウトしますか？"):
            self.session_manager.logout()
            # ログイン画面に戻る
            self.app.show_login()

    def show_profile(self):
        """自分のプロフィール画面の表示（画面遷移版）"""
        try:
            # 現在の画面をクリア
            for widget in self.parent.winfo_children():
                widget.destroy()
            
            # 現在のユーザー情報を取得
            current_user = self.session_manager.get_current_user()
            
            # プロフィール画面を表示（user_id=Noneで自分のプロフィール）
            from views.profile_view import ProfileView
            profile_view = ProfileView(
                parent=self.parent,
                session_manager=self.session_manager,
                app=self.app,
                user_id=None  # 自分のプロフィールを表示するためNoneを指定
            )
            profile_view.show()
            
        except Exception as e:
            logging.error(f"プロフィール画面表示エラー - ユーザー: {current_user['username']} - {e}")
            messagebox.showerror(
                "エラー", 
                f"プロフィール画面の表示中にエラーが発生しました: {e}"
            )
            
    def show_user_profile(self, user_id):
        """他のユーザーのプロフィール画面を表示（画面遷移版）"""
        try:
            # 現在の画面をクリア
            for widget in self.parent.winfo_children():
                widget.destroy()
            
            # プロフィール画面を表示
            from views.profile_view import ProfileView
            profile_view = ProfileView(self.parent, self.session_manager, self.app, user_id=user_id)
            profile_view.show()
        except Exception as e:
            messagebox.showerror("エラー", f"ユーザープロフィール画面の表示中にエラーが発生しました: {e}")

    def show_timeline(self):
        """タイムライン画面の表示"""
        try:
            from views.timeline_view import TimelineView  # 遅延インポート
            for widget in self.parent.winfo_children():
                widget.destroy()
            timeline_view = TimelineView(self.parent, self.session_manager, self.app)
            timeline_view.show()
        except Exception as e:
            messagebox.showerror("エラー", f"タイムライン画面の表示中にエラーが発生しました: {e}")

    def show_search(self):
        """検索画面の表示"""
        try:
            from views.search_view import SearchView  # 遅延インポート
            for widget in self.parent.winfo_children():
                widget.destroy()
            search_view = SearchView(self.parent, self.session_manager, self.app)
            search_view.show()
        except Exception as e:
            messagebox.showerror("エラー", f"検索画面の表示中にエラーが発生しました: {e}")

    def show(self):
        self.frame.pack(fill=tk.BOTH, expand=True)
    
    def search_hashtag(self, hashtag):
        """ハッシュタグがクリックされたときの処理"""
        try:
            # 現在のビューをクリア
            for widget in self.frame.winfo_children():
                widget.destroy()
            # 検索ビューを表示してハッシュタグ検索を実行
            search_view = SearchView(self.frame, self.session_manager, self.app)
            search_view.search_type.set("hashtag")
            search_view.search_entry.insert(0, hashtag)
            search_view.search()
            search_view.show()
        except Exception as e:
            messagebox.showerror("エラー", 
                            f"ハッシュタグ検索中にエラーが発生しました: {e}")
    
    def highlight_hashtags(self, event):
        """投稿テキスト内のハッシュタグをリアルタイムでハイライト"""
        # 既存のハッシュタグ強調表示をクリア
        self.post_text.tag_remove("hashtag", "1.0", tk.END)

        # テキスト全体を取得
        content = self.post_text.get("1.0", tk.END)
        
        # 単語単位で処理
        start = "1.0"
        for word in content.split():
            if word.startswith('#'):
                # ハッシュタグの位置を検索
                pos = self.post_text.search(word, start, tk.END)
                if pos:
                    # ハッシュタグの終わりの位置を計算
                    end = f"{pos}+{len(word)}c"
                    # タグを適用
                    self.post_text.tag_add("hashtag", pos, end)
            if word:
                # 次の検索開始位置を更新
                start = self.post_text.search(word, start, tk.END)
                if start:
                    start = f"{start}+{len(word)}c"
                    
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
    
    
    def show_search_view(self):
        """検索画面への遷移"""
        try:
            from views.search_view import SearchView
            for widget in self.parent.winfo_children():
                widget.destroy()
            search_view = SearchView(self.parent, self.session_manager, self.app)
            search_view.show()
        except Exception as e:
            messagebox.showerror("エラー", f"検索画面の表示中にエラーが発生しました: {e}")