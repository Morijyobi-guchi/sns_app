import tkinter as tk
from tkinter import ttk, messagebox
import sys
import traceback
from views.login_view import LoginView
from views.timeline_view import TimelineView
from views.register_view import RegisterView
from views.profile_view import ProfileView
from views.search_view import SearchView
from utils.session import SessionManager
from views.password_reset_view import PasswordResetView

class SNSApplication:
    def __init__(self):
        try:
            # Root windowの設定
            self.root = tk.Tk()
            self.root.title("最終課題 X")
            self.root.geometry("800x600")
            
            # エラーハンドリング設定
            sys.excepthook = self.handle_exception
            
            # セッション管理の初期化
            self.session_manager = SessionManager()
            
            # メインフレームの設定
            self.main_frame = ttk.Frame(self.root)
            self.main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 初期画面の表示
            self.show_login()
            
        except Exception as e:
            self.handle_exception(type(e), e, e.__traceback__)

    def setup_styles(self):
        """スタイルの設定"""
        style = ttk.Style()
        
        # 危険な操作用のボタンスタイル
        style.configure(
            "Danger.TButton",
            foreground="red",
            padding=5
        )
        
        # 通常のボタンスタイル
        style.configure(
            "TButton",
            padding=5
        )
        
        # フォームのラベルスタイル
        style.configure(
            
            "TLabel",
            padding=5
        )
        
        # 警告用のラベルスタイル
        style.configure(
            "Warning.TLabel",
            foreground="red",
            padding=5
        )

    def show_login(self):
        """ログイン画面の表示"""
        try:
            self._clear_frame()
            LoginView(
                self.main_frame,
                self.session_manager,
                self.on_login_success,
                self.show_register,  # show_register メソッドを渡す
                self.show_password_reset  # show_password_reset メソッドを渡す
            )
        except Exception as e:
            self.handle_exception(type(e), e, e.__traceback__)

    def show_register(self):
        """新規登録画面の表示"""
        try:
            self._clear_frame()
            RegisterView(
                self.main_frame,
                self.session_manager,
                self.show_login  # show_login メソッドを渡す
            )
        except Exception as e:
            self.handle_exception(type(e), e, e.__traceback__)
    
    def show_password_reset(self):
        """パスワードリセット画面の表示"""
        try:
            self._clear_frame()
            PasswordResetView(
                self.main_frame,
                self.show_login  # show_login メソッドを渡す
            )
        except Exception as e:
            self.handle_exception(type(e), e, e.__traceback__)

    def show_timeline(self):
        """タイムライン画面の表示"""
        try:
            self._clear_frame()
            TimelineView(
                self.main_frame,
                self.session_manager,
                self  # app 引数を渡す
            )
        except Exception as e:
            self.handle_exception(type(e), e, e.__traceback__)

    def show_profile(self):
        """プロフィール画面の表示"""
        try:
            self._clear_frame()
            ProfileView(self.main_frame, self.session_manager)
        except Exception as e:
            self.handle_exception(type(e), e, e.__traceback__)

    def show_search(self):
        """検索画面の表示"""
        try:
            self._clear_frame()
            SearchView(self.main_frame, self.session_manager)
        except Exception as e:
            self.handle_exception(type(e), e, e.__traceback__)

    def on_login_success(self, user_data):
        """ログイン成功時の処理"""
        try:
            self.session_manager.login(user_data)
            self.show_timeline()  # タイムライン画面に遷移
        except Exception as e:
            self.handle_exception(type(e), e, e.__traceback__)

    def _clear_frame(self):
        """メインフレームのクリア"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """例外処理"""
        if issubclass(exc_type, KeyboardInterrupt):
            self.root.quit()
        else:
            messagebox.showerror("エラー", f"予期せぬエラーが発生しました: {exc_value}")
            traceback.print_exception(exc_type, exc_value, exc_traceback)

    def run(self):
        """アプリケーションの実行"""
        try:
            self.root.mainloop()
        except Exception as e:
            self.handle_exception(type(e), e, e.__traceback__)

if __name__ == "__main__":
    try:
        # グローバル変数の宣言
        global app
        print("Starting application...")  # デバッグ用
        app = SNSApplication()
        print("Application instance created")  # デバッグ用
        app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()