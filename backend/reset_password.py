import os
import sqlite3
import sys

BACKEND_DIR = os.path.dirname(__file__)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from auth import hash_password
from database import get_user_by_email, create_user

DB_PATH = os.path.join(BACKEND_DIR, 'database', 'documents.db')

def reset_user_password(email, new_password):
    """Reset a user's password"""
    existing_user = get_user_by_email(email)
    if not existing_user:
        print(f"User not found: {email}")
        return False

    new_hash = hash_password(new_password)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_hash, email))
    conn.commit()
    conn.close()
    
    print(f"Password reset for {email}")
    return True

def create_test_user():
    """Create a test user with known credentials"""
    email = "test@example.com"
    password = "test123"
    name = "Test User"
    
    hashed = hash_password(password)
    success = create_user(name, email, hashed)
    
    if success:
        print(f"Created test user: {email} with password: {password}")
    else:
        print(f"User {email} already exists")
    
    return success

if __name__ == "__main__":
    # Reset the existing user's password to a known value
    reset_user_password("mini.ktg1@gmail.com", "password123")
    
    # Also create a test user
    create_test_user()
