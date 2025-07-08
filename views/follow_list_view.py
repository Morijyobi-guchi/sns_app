import tkinter as tk
from tkinter import ttk, messagebox

class FollowListView:
    def __init__(self, parent, session_manager, app, user_id):
        """フォローリストビューの初期化"""
        self.parent = parent
        self.session_manager = session_manager
        self.app = app
        self.user_id = user_id
        self.current_user = session_manager.get_current_user()
        
        # モデルのインスタンス化
        from models.follow import Follow
        from models.user import User
        self.follow_model = Follow()
        self.user_model = User()

        # フォロー情報の取得
        self.following_list = self.follow_model.get_following(self.user_id)
        self.followers_list = self.follow_model.get_followers(self.user_id)

        print(f"Following count: {len(self.following_list) if self.following_list else 0}")  # デバッグ出力
        print(f"Followers count: {len(self.followers_list) if self.followers_list else 0}")  # デバッグ出力

        # メインフレームの作成
        self.create_widgets()

    def create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        self.frame = ttk.Frame(self.parent, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # ヘッダー（戻るボタン）
        self.create_header()

        # タブの作成
        self.create_tabs()

    def create_list_frame(self, parent, users, is_following_list=True):
        """リストフレームの作成（共通処理）"""
        # コンテナフレーム
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # キャンバスとスクロールバー
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # スクロール設定
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # キャンバスの設定
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # ユーザーリストの表示
        if not users:
            message = "フォロー中のユーザーはいません" if is_following_list else "フォロワーはいません"
            ttk.Label(
                scrollable_frame,
                text=message,
                font=('Helvetica', 10)
            ).pack(pady=20, padx=10)
        else:
            for user in users:
                self.create_user_item(scrollable_frame, user, is_following_list)

        # レイアウト
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # マウスホイールでのスクロール
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        return container

    def create_user_item(self, parent, user, is_following_list):
        """ユーザー項目の作成"""
        user_frame = ttk.Frame(parent)
        user_frame.pack(fill=tk.X, pady=5, padx=10)

        # ユーザー名ボタン
        username_button = ttk.Button(
            user_frame,
            text=user['username'],
            command=lambda: self.show_user_profile(user['user_id']),
            width=30
        )
        username_button.pack(side=tk.LEFT, padx=5)

        # フォロー解除ボタン（フォロー中リストかつ自分のリストの場合のみ）
        if is_following_list and self.user_id == self.current_user['user_id']:
            unfollow_button = ttk.Button(
                user_frame,
                text="フォロー解除",
                command=lambda: self.unfollow_user(user['user_id']),
                width=15
            )
            unfollow_button.pack(side=tk.RIGHT, padx=5)

    def create_tabs(self):
        """タブの作成"""
        self.tab_control = ttk.Notebook(self.frame)
        
        # フォロー中タブ
        following_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(following_tab, text=f'フォロー中 ({len(self.following_list) if self.following_list else 0})')
        self.create_list_frame(following_tab, self.following_list, True)

        # フォロワータブ
        followers_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(followers_tab, text=f'フォロワー ({len(self.followers_list) if self.followers_list else 0})')
        self.create_list_frame(followers_tab, self.followers_list, False)

        self.tab_control.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

    def create_header(self):
        """ヘッダーの作成"""
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # 戻るボタン
        back_button = ttk.Button(
            header_frame,
            text="← プロフィールに戻る",
            command=self.back_to_profile
        )
        back_button.pack(side=tk.LEFT)

        # ユーザー名の表示
        user = self.user_model.get_user(self.user_id)
        if user:
            username_label = ttk.Label(
                header_frame,
                text=f"{user['username']}のフォロー/フォロワー",
                font=('Helvetica', 12, 'bold')
            )
            username_label.pack(side=tk.LEFT, padx=20)

    def unfollow_user(self, target_user_id):
        """ユーザーのフォロー解除"""
        try:
            self.follow_model.unfollow_user(
                self.current_user['user_id'],
                target_user_id
            )
            messagebox.showinfo("成功", "フォローを解除しました")
            # フォロー情報を再取得
            self.following_list = self.follow_model.get_following(self.user_id)
            self.followers_list = self.follow_model.get_followers(self.user_id)
            # タブを再作成
            self.refresh_tabs()
        except Exception as e:
            messagebox.showerror("エラー", f"フォロー解除中にエラーが発生しました: {e}")

    def refresh_tabs(self):
        """タブの更新"""
        # 現在選択されているタブのインデックスを保存
        current_tab = self.tab_control.index(self.tab_control.select())
        
        # 既存のタブを削除
        for tab in self.tab_control.winfo_children():
            tab.destroy()
        
        # タブを再作成
        self.create_tabs()
        
        # 保存していたタブを選択
        self.tab_control.select(current_tab)

    def show_user_profile(self, user_id):
        """ユーザープロフィールの表示"""
        try:
            from views.profile_view import ProfileView
            for widget in self.parent.winfo_children():
                widget.destroy()
            profile_view = ProfileView(self.parent, self.session_manager, self.app, user_id)
            profile_view.show()
        except Exception as e:
            messagebox.showerror("エラー", f"プロフィール表示中にエラーが発生しました: {e}")

    def back_to_profile(self):
        """プロフィール画面に戻る"""
        try:
            from views.profile_view import ProfileView
            for widget in self.parent.winfo_children():
                widget.destroy()
            profile_view = ProfileView(self.parent, self.session_manager, self.app, self.user_id)
            profile_view.show()
        except Exception as e:
            messagebox.showerror("エラー", f"プロフィール画面の表示中にエラーが発生しました: {e}")

    def show(self):
        """画面の表示"""
        self.frame.tkraise()