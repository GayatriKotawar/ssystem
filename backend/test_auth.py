from auth import check_password, get_user_by_email

# Test authentication for the user
email = "mini.ktg1@gmail.com"
test_password = "password123"  # Common test password

print(f"Testing authentication for: {email}")

# Get user from database
user = get_user_by_email(email)
if user:
    print(f"User found: {user['name']}")
    print(f"Stored hash: {user['password_hash'][:50]}...")
    
    # Test password verification
    is_valid = check_password(test_password, user['password_hash'])
    print(f"Password '{test_password}' valid: {is_valid}")
    
    # Try some other common passwords
    for pwd in ["123456", "password", "admin", "mini", "ktg1"]:
        is_valid = check_password(pwd, user['password_hash'])
        if is_valid:
            print(f"Found correct password: '{pwd}'")
            break
else:
    print("User not found in database")
