from config.database import BaseModel
import logging

logger = logging.getLogger(__name__)

class Follow(BaseModel):
    def __init__(self):
        super().__init__()

    def follow_user(self, follower_id, followed_id):
        """ユーザーをフォローする"""
        query = """
        INSERT INTO follows (follower_id, followed_id)
        VALUES (%s, %s)
        """
        try:
            self.db.execute_update(query, (follower_id, followed_id))
        except Exception as e:
            raise ValueError(f"フォローに失敗しました: {e}")

    def unfollow_user(self, follower_id, followed_id):
        """ユーザーのフォローを解除する"""
        query = """
        DELETE FROM follows WHERE follower_id = %s AND followed_id = %s
        """
        try:
            self.db.execute_update(query, (follower_id, followed_id))
        except Exception as e:
            raise ValueError(f"フォロー解除に失敗しました: {e}")

    def get_followers(self, user_id):
        """フォロワーの一覧を取得する"""
        query = """
        SELECT users.user_id, users.username FROM follows
        JOIN users ON follows.follower_id = users.user_id
        WHERE follows.followed_id = %s
        ORDER BY users.username
        """
        try:
            return self.db.execute_query(query, (user_id,))
        except Exception as e:
            print(f"Error getting followers: {e}")
            return []

    def get_following(self, user_id):
        """フォローしているユーザーの一覧を取得する"""
        query = """
        SELECT users.user_id, users.username FROM follows
        JOIN users ON follows.followed_id = users.user_id
        WHERE follows.follower_id = %s
        ORDER BY users.username
        """
        try:
            return self.db.execute_query(query, (user_id,))
        except Exception as e:
            print(f"Error getting following: {e}")
            return []

    def is_following(self, follower_id, followed_id):
        """ユーザーがフォローしているかどうかを確認する"""
        query = """
        SELECT 1 FROM follows 
        WHERE follower_id = %s AND followed_id = %s
        """
        try:
            result = self.db.execute_query(query, (follower_id, followed_id))
            return len(result) > 0
        except Exception as e:
            print(f"Error checking follow status: {e}")
            return False

    def get_follower_count(self, user_id):
        """フォロワー数を取得する"""
        query = """
        SELECT COUNT(*) as count FROM follows
        WHERE followed_id = %s
        """
        try:
            result = self.db.execute_query(query, (user_id,))
            return result[0]['count'] if result else 0
        except Exception as e:
            print(f"Error getting follower count: {e}")
            return 0

    def get_following_count(self, user_id):
        """フォロー中のユーザー数を取得する"""
        query = """
        SELECT COUNT(*) as count FROM follows
        WHERE follower_id = %s
        """
        try:
            result = self.db.execute_query(query, (user_id,))
            return result[0]['count'] if result else 0
        except Exception as e:
            print(f"Error getting following count: {e}")
            return 0