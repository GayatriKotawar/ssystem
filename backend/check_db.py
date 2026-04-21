import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'documents.db')

def check_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if users table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = c.fetchone()
    
    if table_exists:
        print("Users table exists")
        c.execute("SELECT email, name FROM users;")
        users = c.fetchall()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  - Email: {user[0]}, Name: {user[1]}")
    else:
        print("Users table does not exist")
    
    conn.close()

if __name__ == "__main__":
    check_users()
