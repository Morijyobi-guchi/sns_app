from config.database import BaseModel

class Like(BaseModel):
    def __init__(self):
        super().__init__()

    def toggle_like(self, user_id, post_id):
        """いいねの切り替え"""
        query_check = """
        SELECT * FROM likes WHERE user_id = %s AND post_id = %s
        """
        query_add = """
        INSERT INTO likes (user_id, post_id) VALUES (%s, %s)
        """
        query_remove = """
        DELETE FROM likes WHERE user_id = %s AND post_id = %s
        """
        
        try:
            result = self.db.execute_query(query_check, (user_id, post_id))
            if result:
                self.db.execute_update(query_remove, (user_id, post_id))
                return False  # いいねを取り消した
            else:
                self.db.execute_update(query_add, (user_id, post_id))
                return True  # いいねを追加した
        except Exception as e:
            raise ValueError(f"いいねの切り替えに失敗しました: {e}")

    def get_like_count(self, post_id):
        """特定の投稿のいいね数を取得"""
        query = """
        SELECT COUNT(*) as like_count FROM likes WHERE post_id = %s
        """
        result = self.db.execute_query(query, (post_id,))
        return result[0]['like_count'] if result else 0