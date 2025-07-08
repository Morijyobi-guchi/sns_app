from datetime import datetime
from config.database import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Post(BaseModel):
    def __init__(self):
        super().__init__()

    def create_post(self, user_id, content):
        """新規投稿の作成"""
        query = """
        INSERT INTO posts (user_id, content, created_at)
        VALUES (%s, %s, %s)
        """
        created_at = datetime.now()
        try:
            post_id = self.db.execute_update(query, (user_id, content, created_at))
            return self.get_post(post_id)
        except Exception as e:
            raise ValueError(f"投稿の作成に失敗しました: {e}")

    def get_post(self, post_id):
        """特定の投稿を取得"""
        query = """
        SELECT p.*, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.user_id
        WHERE p.post_id = %s
        """
        posts = self.db.execute_query(query, (post_id,))
        return posts[0] if posts else None

    def get_timeline_posts(self, user_id):
        """タイムラインの投稿を取得（フォロー中のユーザーと自分の投稿）"""
        query = """
        SELECT 
            p.*,
            u.username,
            COUNT(DISTINCT l.user_id) as like_count,
            COUNT(DISTINCT c.comment_id) as comment_count,
            u.user_id as author_id
        FROM posts p
        JOIN users u ON p.user_id = u.user_id
        LEFT JOIN likes l ON p.post_id = l.post_id
        LEFT JOIN comments c ON p.post_id = c.post_id
        WHERE p.user_id IN (
            -- フォロー中のユーザーのID
            SELECT followed_id 
            FROM follows 
            WHERE follower_id = %s
            UNION
            -- 自分のID
            SELECT %s
        )
        GROUP BY p.post_id, p.user_id, p.content, p.created_at, u.username, u.user_id
        ORDER BY p.created_at DESC
        """
        
        try:
            result = self.db.execute_query(query, (user_id, user_id))
            logging.debug(f"Retrieved {len(result) if result else 0} posts for timeline")
            return result
        except Exception as e:
            logging.error(f"Error getting timeline posts: {e}")
            return []

    def update_post(self, post_id, content):
        """投稿の更新"""
        query = """
        UPDATE posts SET content = %s, updated_at = %s WHERE post_id = %s
        """
        updated_at = datetime.now()
        try:
            self.db.execute_update(query, (content, updated_at, post_id))
        except Exception as e:
            raise ValueError(f"投稿の更新に失敗しました: {e}")

    def get_user_posts(self, user_id):
        """特定のユーザーの投稿を取得"""
        query = """
        SELECT p.*, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.user_id
        WHERE p.user_id = %s
        ORDER BY p.created_at DESC
        """
        return self.db.execute_query(query, (user_id,))

    def search_posts_by_hashtag(self, hashtag):
        """ハッシュタグで投稿を検索"""
        try:
            # クエリの修正：タイムスタンプでソート
            query = """
                SELECT 
                    p.*,
                    u.username,
                    u.user_id,
                    p.created_at
                FROM posts p
                JOIN users u ON p.user_id = u.user_id
                WHERE p.content LIKE %s
                ORDER BY p.created_at DESC
            """
            
            # ハッシュタグの検索条件を調整
            search_term = f"%{hashtag}%"
            results = self.db.execute_query(query, (search_term,))
            
            logging.info(f"Hashtag search for {hashtag}: Found {len(results)} posts")
            return results

        except Exception as e:
            logging.error(f"ハッシュタグ検索中にエラーが発生しました: {e}")
            raise Exception(f"ハッシュタグ検索中にエラーが発生しました: {e}")
    
    def get_following_posts(self, user_id):
        """フォロー中のユーザーと自分の投稿を取得"""
        return self.get_timeline_posts(user_id)