import bcrypt
from database import get_user_by_email, create_user

def hash_password(password: str) -> str:
    """Hashes a password with bcrypt."""
    # bcrypt requires bytes
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    """Verifies a password against a hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(name: str, email: str, password: str) -> bool:
    """Registers a new user, hashes password. Returns False if user exists."""
    hashed = hash_password(password)
    return create_user(name, email, hashed)

def authenticate_user(email: str, password: str):
    """Authenticates a user by email and password. Returns user dict or None."""
    user = get_user_by_email(email)
    if not user:
        return None
        
    if check_password(password, user['password_hash']):
        return user
    return None
