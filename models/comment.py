from config.database import BaseModel
from datetime import datetime

class Comment(BaseModel):
    def __init__(self):
        super().__init__()

    def create_comment(self, user_id, post_id, content):
        """新規コメントの作成"""
        query = """
        INSERT INTO comments (user_id, post_id, content, created_at)
        VALUES (%s, %s, %s, %s)
        """
        created_at = datetime.now()
        try:
            comment_id = self.db.execute_update(query, (user_id, post_id, content, created_at))
            return self.get_comment(comment_id)
        except Exception as e:
            raise ValueError(f"コメントの作成に失敗しました: {e}")

    def get_comment(self, comment_id):
        """特定のコメントを取得"""
        query = """
        SELECT c.*, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.user_id
        WHERE c.comment_id = %s
        """
        comments = self.db.execute_query(query, (comment_id,))
        return comments[0] if comments else None

    def get_comments_for_post(self, post_id):
        """特定の投稿に対するコメントを取得"""
        query = """
        SELECT c.*, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.user_id
        WHERE c.post_id = %s
        ORDER BY c.created_at ASC
        """
        return self.db.execute_query(query, (post_id,))
    
    
    def get_comment_count(self, post_id):
        """特定の投稿のコメント数を取得"""
        query = """
        SELECT COUNT(*) as comment_count FROM comments WHERE post_id = %s
        """
        result = self.db.execute_query(query, (post_id,))
        return result[0]['comment_count'] if result else 0