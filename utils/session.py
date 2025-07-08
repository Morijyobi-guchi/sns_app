class SessionManager:
    def __init__(self):
        self.current_user = None

    def login(self, user_data):
        """ユーザーのログイン"""
        self.current_user = {
            'user_id': user_data['user_id'],
            'username': user_data['username']
        }

    def logout(self):
        """ユーザーのログアウト"""
        self.current_user = None

    def get_current_user(self):
        """現在のユーザーを取得"""
        return self.current_user

    def update_current_user(self, username):
        """現在のユーザー情報を更新"""
        if self.current_user:
            self.current_user['username'] = username
    
    def set_current_user(self, user):
        """現在のログインユーザーを設定"""
        self.current_user = user

    def is_logged_in(self):
        """ログイン状態をチェック"""
        return self.current_user is not None