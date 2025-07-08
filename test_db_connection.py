# test_db_connection.py
import sys
import traceback
import time

def test_mysql_connection():
    print("Starting database connection test...")
    print(f"Python version: {sys.version}")
    
    try:
        print("Importing mysql.connector...")
        import mysql.connector
        print(f"mysql.connector version: {mysql.connector.__version__}")
        
        print("\nAttempting to connect to MySQL database...")
        connection_config = {
            "host": "localhost",
            "user": "root",
            "password": "morijyobi",
            "database": "sns_app",
            "raise_on_warnings": True,
            "connection_timeout": 10
        }
        
        # 接続前の待機
        time.sleep(1)
        
        try:
            connection = mysql.connector.connect(**connection_config)
            
            if connection.is_connected():
                db_info = connection.get_server_info()
                print(f"Connected to MySQL Server version {db_info}")
                
                cursor = connection.cursor()
                
                # データベース名の確認
                cursor.execute("SELECT DATABASE()")
                database = cursor.fetchone()
                print(f"Connected to database: {database[0]}")
                
                # テーブル一覧の表示
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print("\nAvailable tables:")
                for table in tables:
                    print(f"- {table[0]}")
                    
        except mysql.connector.Error as err:
            print(f"MySQL Error: {err}")
            print(f"Error Code: {err.errno}")
            print(f"SQLSTATE: {err.sqlstate}")
            print(f"Error Message: {err.msg}")
            return False
            
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                print("\nMySQL connection is closed")
                
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False
        
    return True

if __name__ == "__main__":
    success = test_mysql_connection()
    if not success:
        sys.exit(1)