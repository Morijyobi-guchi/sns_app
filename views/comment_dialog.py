import tkinter as tk
from tkinter import ttk, messagebox
from models.comment import Comment

class CommentDialog(tk.Toplevel):
    def __init__(self, parent, post_id, session_manager, refresh_callback=None):  # refresh_callbackを追加
        super().__init__(parent)
        self.parent = parent
        self.post_id = post_id
        self.session_manager = session_manager
        self.comment_model = Comment()
        self.refresh_callback = refresh_callback  # コールバック関数を保存

        self.title("コメント")
        self.geometry("400x400")
        self.create_widgets()
        self.load_comments()

    def create_widgets(self):
        self.frame = ttk.Frame(self, padding="10")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # コメント表示エリア
        self.comment_listbox = tk.Listbox(self.frame)
        self.comment_listbox.pack(fill=tk.BOTH, expand=True)

        # コメント入力エリア
        self.comment_entry = tk.Entry(self.frame)
        self.comment_entry.pack(fill=tk.X, pady=(10, 0))

        # 送信ボタン
        send_button = ttk.Button(self.frame, text="送信", command=self.on_send)
        send_button.pack(anchor=tk.E, pady=(5, 0))

    def load_comments(self):
        """コメントの読み込み"""
        try:
            comments = self.comment_model.get_comments_for_post(self.post_id)
            self.comment_listbox.delete(0, tk.END)
            for comment in comments:
                self.comment_listbox.insert(tk.END, f"{comment['username']}: {comment['content']}")
        except Exception as e:
            messagebox.showerror("エラー", f"コメントの読み込み中にエラーが発生しました: {e}")

    def on_send(self):
        """コメントの送信処理"""
        content = self.comment_entry.get().strip()
        if not content:
            messagebox.showwarning("警告", "コメント内容を入力してください。")
            return

        try:
            user = self.session_manager.get_current_user()
            self.comment_model.create_comment(user['user_id'], self.post_id, content)
            self.comment_entry.delete(0, tk.END)
            self.load_comments()
            
            # タイムラインの更新
            if self.refresh_callback:
                self.refresh_callback()
            
        except Exception as e:
            messagebox.showerror("エラー", f"コメントの送信中にエラーが発生しました: {e}")