# test_pymysql.py
import pymysql
import sys

def test_pymysql_connection():
    try:
        print("Attempting to connect using PyMySQL...")
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='morijyobi',
            database='sns_app',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"Database version: {version['VERSION()']}")
                
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print("\nAvailable tables:")
                for table in tables:
                    print(f"- {list(table.values())[0]}")
                    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_pymysql_connection()