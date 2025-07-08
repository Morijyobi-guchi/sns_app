import bcrypt
from config.database import BaseModel
import logging
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error

logging.basicConfig(level=logging.DEBUG)  # デバッグレベルに変更
logger = logging.getLogger(__name__)

class User(BaseModel):
    def __init__(self):
        super().__init__()

    def hash_password(self, password):
        """パスワードをbcryptでハッシュ化し、ハッシュとソルトを生成"""
        # パスワードをバイト列に変換
        password_bytes = password.encode('utf-8')
        # ソルトを生成
        salt = bcrypt.gensalt()
        # ハッシュ化
        password_hash = bcrypt.hashpw(password_bytes, salt)
        
        return {
            'password_hash': password_hash.decode('utf-8'),
            'salt': salt.decode('utf-8')
        }
        
    def create_user(self, username, email, password, activation_code=None):
        """ユーザーを作成"""
        try:
            # 重複チェック
            check_query = "SELECT 1 FROM users WHERE username = %s OR email = %s"
            result = self.db.execute_query(check_query, (username, email))
            if result:
                raise Exception("このユーザー名またはメールアドレスは既に使用されています")

            # パスワードハッシュ化
            password_data = self.hash_password(password)
            
            # ユーザー作成
            insert_query = """
                INSERT INTO users (username, email, password_hash, salt, activation_code, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            params = (
                username, 
                email, 
                password_data['password_hash'],
                password_data['salt'],
                activation_code,
                False
            )
            
            return self.db.execute_update(insert_query, params)
                
        except Exception as e:
            raise Exception(f"ユーザーの作成に失敗しました: {e}")
        
    def verify_password(self, user_id, provided_password):
        """パスワードを検証"""
        try:
            # ユーザーのパスワードハッシュとソルトを取得
            query = "SELECT password_hash, salt FROM users WHERE user_id = %s"
            result = self.db.execute_query(query, (user_id,))
            
            if not result:
                return False
                
            stored_hash = result[0]['password_hash']
            stored_salt = result[0]['salt']
            
            # 提供されたパスワードをバイト列に変換
            password_bytes = provided_password.encode('utf-8')
            stored_hash_bytes = stored_hash.encode('utf-8')
            stored_salt_bytes = stored_salt.encode('utf-8')
            
            # 提供されたパスワードをハッシュ化して比較
            hashed = bcrypt.hashpw(password_bytes, stored_salt_bytes)
            return hashed == stored_hash_bytes
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False
        
    def authenticate(self, username, password):
        """ユーザー認証"""
        connection = None
        try:
            connection = self.db.create_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()

                if not user:
                    return None

                if self._verify_password(password, user['password_hash']):
                    # セキュリティのため、センシティブな情報を削除
                    del user['password_hash']
                    del user['salt']
                    return user
                return None
        finally:
            if connection:
                connection.close()

    def _check_duplicate(self, username, email):
        """ユーザー名とメールアドレスの重複チェック"""
        query = "SELECT 1 FROM users WHERE username = %s OR email = %s"
        result = self.db.execute_query(query, (username, email))
        return bool(result)

    def _verify_password(self, password, stored_hash):
        """パスワードの検証"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                stored_hash.encode('utf-8')
            )
        except Exception:
            return False

    def get_user(self, user_id):
        """特定のユーザーを取得"""
        query = "SELECT * FROM users WHERE user_id = %s"
        users = self.db.execute_query(query, (user_id,))
        return users[0] if users else None

    def get_user_by_username(self, username):
        """特定のユーザー名でユーザーを取得"""
        query = "SELECT * FROM users WHERE username = %s"
        users = self.db.execute_query(query, (username,))
        return users[0] if users else None

    def search_users(self, query):
        """ユーザーの検索"""
        query = f"%{query}%"
        sql = "SELECT user_id, username FROM users WHERE username LIKE %s"
        try:
            return self.db.execute_query(sql, (query,))
        except Exception as e:
            raise ValueError(f"ユーザーの検索に失敗しました: {e}")

        
    def get_user_by_id(self, user_id):
        """IDでユーザーを取得"""
        connection = None
        try:
            connection = self.db.create_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                user = cursor.fetchone()
                if user:
                    # セキュリティのため、センシティブな情報を削除
                    del user['password_hash']
                    del user['salt']
                return user
        finally:
            if connection:
                connection.close()

    def get_user_by_email(self, email):
        """メールアドレスでユーザーを取得"""
        connection = None
        try:
            connection = self.db.create_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                if user:
                    # セキュリティのため、センシティブな情報を削除
                    del user['password_hash']
                    del user['salt']
                return user
        finally:
            if connection:
                connection.close()
    
    def username_exists(self, username):
        """ユーザー名が既に存在するかチェック"""
        try:
            query = "SELECT COUNT(*) as count FROM users WHERE username = %s"
            result = self.db.execute_query(query, (username,))
            return result[0]['count'] > 0
        except Exception as e:
            raise Exception(f"ユーザー名チェックに失敗しました: {e}")

    def email_exists(self, email):
        """メールアドレスが既に存在するかチェック"""
        try:
            query = "SELECT COUNT(*) as count FROM users WHERE email = %s"
            result = self.db.execute_query(query, (email,))
            return result[0]['count'] > 0
        except Exception as e:
            raise Exception(f"メールアドレスチェックに失敗しました: {e}")

    def update_user(self, user_id, updates):
        """ユーザー情報の更新"""
        try:
            # ユーザー名の更新がある場合は重複チェック
            if 'username' in updates:
                query = "SELECT user_id FROM users WHERE username = %s AND user_id != %s"
                result = self.db.execute_query(query, (updates['username'], user_id))
                if result:
                    raise Exception("このユーザー名は既に使用されています。")

            # パスワードの更新がある場合はハッシュ化
            if 'password' in updates:
                password_data = self.hash_password(updates['password'])
                updates['password_hash'] = password_data['password_hash']
                updates['salt'] = password_data['salt']
                del updates['password']

            # UPDATE文の作成
            set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
            values = list(updates.values())
            values.append(user_id)

            query = f"UPDATE users SET {set_clause} WHERE user_id = %s"
            self.db.execute_update(query, values)

            return True

        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise

    def delete_user(self, user_id):
        """ユーザーとその関連データを削除"""
        try:
            # 関連データの削除（カスケード削除が設定されていない場合）
            # いいねの削除
            self.db.execute_update(
                "DELETE FROM likes WHERE user_id = %s",
                (user_id,)
            )
            
            # コメントの削除
            self.db.execute_update(
                "DELETE FROM comments WHERE user_id = %s",
                (user_id,)
            )
            
            # フォロー関係の削除
            self.db.execute_update(
                "DELETE FROM follows WHERE follower_id = %s OR followed_id = %s",
                (user_id, user_id)
            )
            
            # 投稿の削除（post_hashtagsはCASCADE設定済み）
            self.db.execute_update(
                "DELETE FROM posts WHERE user_id = %s",
                (user_id,)
            )
            
            # ユーザーの削除
            self.db.execute_update(
                "DELETE FROM users WHERE user_id = %s",
                (user_id,)
            )
            
            return True
                
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise
        
    def is_username_taken(self, username):
        """指定されたユーザー名が既に使用されているかチェック"""
        try:
            query = "SELECT COUNT(*) as count FROM users WHERE username = %s"
            result = self.db.execute_query(query, (username,))
            return result[0]['count'] > 0

        except Exception as e:
            logger.error(f"Error checking username: {str(e)}")
            raise Exception(f"ユーザー名の確認中にエラーが発生しました: {str(e)}")

    def set_verification_code(self, user_id, code, expiration):
        """認証コードと有効期限を設定"""
        connection = None
        cursor = None
        try:
            # タイムスタンプをMySQLの形式に変換
            expiration_str = expiration.strftime('%Y-%m-%d %H:%M:%S')
            
            query = """
            UPDATE users 
            SET email_verification_code = %s,
                email_verification_expires_at = %s,
                is_email_verified = FALSE
            WHERE user_id = %s
            """
            
            logger.debug(f"Setting verification code for user_id: {user_id}")
            logger.debug(f"Expiration time: {expiration_str}")
            
            connection = self.db.create_connection()
            cursor = connection.cursor()  # dictinaryパラメータを削除
            
            # パラメータのデバッグ出力
            params = (code, expiration_str, user_id)
            
            # クエリ実行
            cursor.execute(query, params)
            affected_rows = cursor.rowcount
            
            if affected_rows == 0:
                logger.error(f"No rows affected for user_id: {user_id}")
                raise Exception(f"ユーザーが見つかりません (ID: {user_id})")
                
            # 変更を確定
            connection.commit()
            
            # 更新の確認
            verify_query = "SELECT user_id FROM users WHERE user_id = %s AND email_verification_code = %s"
            cursor.execute(verify_query, (user_id, code))
            result = cursor.fetchone()
            
            if not result:
                raise Exception("認証コードの保存が確認できません")
                
            logger.info(f"認証コードを保存しました (ユーザーID: {user_id})")
            return True
            
        except Exception as e:
            logger.error(f"認証コード保存エラー: {str(e)}")
            if connection:
                connection.rollback()
            raise Exception(f"認証コードの保存に失敗しました: {str(e)}")
            
        finally:
            try:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()
            except Exception as e:
                logger.error(f"Error closing database connections: {e}")

    def verify_email_code(self, user_id, code):
        """メール認証コードを検証する"""
        connection = None
        cursor = None
        try:
            logger.debug(f"Verifying email code for user_id: {user_id}")
            
            query = """
            SELECT user_id 
            FROM users 
            WHERE user_id = %s 
            AND email_verification_code = %s 
            AND email_verification_expires_at > NOW()
            AND is_email_verified = FALSE
            """
            
            connection = self.db.create_connection()
            cursor = connection.cursor()
            
            cursor.execute(query, (user_id, code))
            result = cursor.fetchone()
            
            if result:
                logger.info(f"Valid verification code for user {user_id}")
                return True
            else:
                logger.warning(f"Invalid or expired verification code for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying email code: {e}")
            raise Exception(f"認証コードの検証に失敗しました: {str(e)}")
            
        finally:
            try:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()
            except Exception as e:
                logger.error(f"Error closing database connections: {e}")
        
    def update_email_verification_status(self, user_id, is_verified):
        """メール認証状態を更新する"""
        connection = None
        cursor = None
        try:
            logger.debug(f"Updating email verification status for user_id: {user_id}")
            
            query = """
            UPDATE users 
            SET is_email_verified = %s,
                email_verification_code = NULL,
                email_verification_expires_at = NULL
            WHERE user_id = %s
            """
            
            connection = self.db.create_connection()
            cursor = connection.cursor()
            
            cursor.execute(query, (is_verified, user_id))
            affected_rows = cursor.rowcount
            
            if affected_rows == 0:
                raise Exception(f"ユーザーが見つかりません (ID: {user_id})")
                
            connection.commit()
            logger.info(f"Email verification status updated for user {user_id}")
            return True
            
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Error updating email verification status: {e}")
            raise Exception(f"認証状態の更新に失敗しました: {str(e)}")
            
        finally:
            try:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()
            except Exception as e:
                logger.error(f"Error closing database connections: {e}")