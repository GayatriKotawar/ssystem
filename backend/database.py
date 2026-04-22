import sqlite3
from datetime import datetime
import os
import json

# DB path inside the database directory
DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'documents.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database with users and documents tables."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            document_category TEXT,
            extracted_data TEXT,
            upload_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_user(name, email, password_hash):
    """Creates a new user. Returns True if successful, False if email exists."""
    conn = get_db_connection()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        c.execute('''
            INSERT INTO users (name, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        ''', (name, email, password_hash, now))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    finally:
        conn.close()
    return success

def get_user_by_email(email):
    """Retrieves user by email."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    conn.close()
    if user:
        return dict(user)
    return None

def save_document(user_id, file_name, file_type, document_category, extracted_data):
    """Saves a processed document for a user."""
    conn = get_db_connection()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Store JSON as string
    data_str = json.dumps(extracted_data)
    
    c.execute('''
        INSERT INTO documents (user_id, file_name, file_type, document_category, extracted_data, upload_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, file_name, file_type, document_category, data_str, now))
    
    conn.commit()
    conn.close()

def get_user_documents(user_id):
    """Retrieves all documents for a specific user as a DataFrame."""
    import pandas as pd

    conn = get_db_connection()
    query = "SELECT * FROM documents WHERE user_id = ? ORDER BY upload_date DESC"
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df
