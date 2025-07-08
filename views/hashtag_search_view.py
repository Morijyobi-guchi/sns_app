# views/hashtag_search_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from models.post import PostModel

class HashtagSearchView:
    def __init__(self, parent, session_manager):
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.session_manager = session_manager
        self.post_model = PostModel()
        
        # 検索エリアの作成
        self.create_search_area()
        
        # 結果表示エリアの作成
        self.create_results_area()
        
        # 人気のハッシュタグ表示
        self.show_trending_hashtags()
    
    def create_search_area(self):
        """検索エリアの作成"""
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # タイトル
        ttk.Label(
            search_frame,
            text="ハッシュタグ検索",
            font=('Helvetica', 16)
        ).pack(pady=10)
        
        # 検索バー
        search_bar_frame = ttk.Frame(search_frame)
        search_bar_frame.pack(fill=tk.X, pady=5)
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_bar_frame,
            textvariable=self.search_var,
            font=('Helvetica', 12)
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # 検索ボタン
        ttk.Button(
            search_bar_frame,
            text="検索",
            command=self.search_hashtags
        ).pack(side=tk.RIGHT)
        
        # 検索のヒント
        ttk.Label(
            search_frame,
            text="※ #なしでも検索できます",
            font=('Helvetica', 8)
        ).pack(pady=(0, 10))
    
    def create_results_area(self):
        """結果表示エリアの作成"""
        # メインフレーム
        self.results_frame = ttk.Frame(self.frame)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(self.results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 結果表示用キャンバス
        self.results_canvas = tk.Canvas(
            self.results_frame,
            yscrollcommand=scrollbar.set
        )
        self.results_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # スクロールバーの設定
        scrollbar.config(command=self.results_canvas.yview)
        
        # 投稿表示用フレーム
        self.posts_frame = ttk.Frame(self.results_canvas)
        self.results_canvas.create_window(
            (0, 0),
            window=self.posts_frame,
            anchor=tk.NW,
            width=self.results_canvas.winfo_width()
        )
        
        # キャンバスのリサイズ設定
        self.posts_frame.bind(
            '<Configure>',
            lambda e: self.results_canvas.configure(
                scrollregion=self.results_canvas.bbox("all")
            )
        )
    
    def search_hashtags(self):
        """ハッシュタグ検索の実行"""
        search_term = self.search_var.get().strip()
        if not search_term:
            messagebox.showwarning("警告", "検索語を入力してください")
            return
        
        # '#'が付いていない場合は付ける
        if not search_term.startswith('#'):
            search_term = f"#{search_term}"
        
        try:
            # 検索結果の取得
            results = self.post_model.search_posts_by_hashtag(search_term)
            
            # 結果の表示
            self.display_results(results)
        except Exception as e:
            messagebox.showerror("エラー", f"検索中にエラーが発生しました: {str(e)}")
    
    def display_results(self, posts):
        """検索結果の表示"""
        # 既存の結果をクリア
        for widget in self.posts_frame.winfo_children():
            widget.destroy()
        
        if not posts:
            ttk.Label(
                self.posts_frame,
                text="該当する投稿が見つかりませんでした",
                font=('Helvetica', 10)
            ).pack(pady=20)
            return
        
        # 投稿の表示
        for post in posts:
            self.create_post_widget(post)
    
    def create_post_widget(self, post):
        """投稿ウィジェットの作成"""
        post_frame = ttk.Frame(self.posts_frame)
        post_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # ユーザー名
        ttk.Label(
            post_frame,
            text=f"@{post['username']}",
            font=('Helvetica', 10, 'bold')
        ).pack(anchor=tk.W)
        
        # 投稿内容
        ttk.Label(
            post_frame,
            text=post['content'],
            wraplength=400
        ).pack(anchor=tk.W, pady=(2, 5))
        
        # 投稿日時
        ttk.Label(
            post_frame,
            text=post['created_at'].strftime('%Y-%m-%d %H:%M'),
            font=('Helvetica', 8)
        ).pack(anchor=tk.E)
        
        # 区切り線
        ttk.Separator(post_frame, orient='horizontal').pack(
            fill=tk.X, pady=5
        )
    
    def show_trending_hashtags(self):
        """人気のハッシュタグを表示"""
        try:
            trending_tags = self.post_model.get_trending_hashtags()
            if trending_tags:
                trending_frame = ttk.Frame(self.frame)
                trending_frame.pack(fill=tk.X, padx=10, pady=5)
                
                ttk.Label(
                    trending_frame,
                    text="トレンド",
                    font=('Helvetica', 12, 'bold')
                ).pack(anchor=tk.W)
                
                for tag in trending_tags:
                    tag_button = ttk.Button(
                        trending_frame,
                        text=tag['tag_name'],
                        command=lambda t=tag['tag_name']: self.search_tag(t)
                    )
                    tag_button.pack(anchor=tk.W, pady=2)
        except Exception as e:
            print(f"トレンド取得エラー: {str(e)}")
    
    def search_tag(self, tag):
        """トレンドタグをクリックして検索"""
        self.search_var.set(tag)
        self.search_hashtags()