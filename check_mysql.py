# check_mysql.py
import subprocess
import platform
import sys

def check_mysql_service():
    system = platform.system()
    print(f"Operating System: {system}")
    
    if system == "Windows":
        try:
            # MySQLのステータスを確認
            result = subprocess.run(
                ['sc', 'query', 'MySQL'],
                capture_output=True,
                text=True
            )
            print("\nMySQL Service Status:")
            print(result.stdout)
            
            # MySQLのプロセスを確認
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq mysqld.exe'],
                capture_output=True,
                text=True
            )
            print("\nMySQL Process Status:")
            print(result.stdout)
            
        except Exception as e:
            print(f"Error checking MySQL service: {e}")
            
if __name__ == "__main__":
    check_mysql_service()