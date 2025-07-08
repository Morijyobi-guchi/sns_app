# test_db_connection.py
import mysql.connector
import sys

def test_mysql_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="morijyobi",
            database="sns_app"
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("select database();")
            database = cursor.fetchone()
            print(f"Connected to database: {database[0]}")
            
            # テーブル一覧を表示
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("\nAvailable tables:")
            for table in tables:
                print(f"- {table[0]}")
                
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        sys.exit(1)
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    test_mysql_connection()