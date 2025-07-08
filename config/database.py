import pymysql
import logging
from datetime import datetime

logging.basicConfig(
    filename='database.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DatabasePool:
    _instance = None
    _pool = None
    
    DB_CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "morijyobi",
        "database": "sns_app",
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor  # ここでDictCursorを指定
    }
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def create_connection(self):
        """新しい接続を作成"""
        try:
            connection = pymysql.connect(**self.DB_CONFIG)
            connection.autocommit(False)  # 自動コミットを無効化
            return connection
        except Exception as e:
            logging.error(f"Error creating database connection: {e}")
            raise
    
    def execute_transaction(self, queries_and_params):
        """トランザクションで複数のクエリを実行"""
        connection = None
        try:
            connection = self.create_connection()
            with connection.cursor() as cursor:
                for query, params in queries_and_params:
                    cursor.execute(query, params or ())
                connection.commit()
                return cursor.lastrowid
        except Exception as e:
            if connection:
                connection.rollback()
            logging.error(f"Transaction execution error: {e}")
            raise
        finally:
            if connection:
                connection.close()

    def execute_query(self, query, params=None):
        """SELECT クエリの実行"""
        connection = None
        try:
            connection = self.create_connection()
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                return result
        except Exception as e:
            logging.error(f"Query execution error: {e}")
            logging.error(f"Query: {query}")
            logging.error(f"Params: {params}")
            raise
        finally:
            if connection:
                connection.close()
    
    def execute_update(self, query, params=None):
        """INSERT/UPDATE/DELETE クエリの実行"""
        connection = None
        try:
            connection = self.create_connection()
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                connection.commit()
                return cursor.lastrowid
        except Exception as e:
            if connection:
                connection.rollback()
            logging.error(f"Update execution error: {e}")
            logging.error(f"Query: {query}")
            logging.error(f"Params: {params}")
            raise
        finally:
            if connection:
                connection.close()
                
    def fetch_one(self, query, params=None):
        """単一行を取得するメソッド"""
        with self.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()

class BaseModel:
    def __init__(self):
        self.db = DatabasePool.get_instance()