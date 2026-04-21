import os
import shutil

def setup_environment():
    """Setup script for the Smart Document Management System"""
    
    print("=== Smart Document Management System Setup ===\n")
    
    # Step 1: Create .env file
    env_file = ".env"
    env_example = ".env.example"
    
    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            shutil.copy(env_example, env_file)
            print(f"1. Created {env_file} from {env_example}")
        else:
            with open(env_file, 'w') as f:
                f.write("# Google Generative AI (Gemini) API Key\n")
                f.write("# Get your API key from: https://ai.google.dev/gemini-api/docs/api-key\n")
                f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
            print(f"1. Created {env_file} template")
    else:
        print(f"1. {env_file} already exists")
    
    # Step 2: Initialize database
    print("\n2. Initializing database...")
    try:
        from database import init_db
        init_db()
        print("   Database initialized successfully")
    except Exception as e:
        print(f"   Database initialization error: {e}")
    
    # Step 3: Check users
    print("\n3. Checking existing users...")
    try:
        from database import get_db_connection
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT email, name FROM users;")
        users = c.fetchall()
        conn.close()
        
        if users:
            print(f"   Found {len(users)} existing users:")
            for email, name in users:
                print(f"   - {email} ({name})")
        else:
            print("   No users found")
    except Exception as e:
        print(f"   Error checking users: {e}")
    
    print("\n=== Setup Complete ===")
    print("\nNext steps:")
    print("1. Get a Gemini API key from: https://ai.google.dev/gemini-api/docs/api-key")
    print("2. Edit the .env file and replace 'your_gemini_api_key_here' with your actual API key")
    print("3. Run the backend server: uvicorn main:app --reload")
    print("4. Run the frontend server (in another terminal): cd frontend && npm start")
    
    print("\nTest credentials:")
    print("- Email: mini.ktg1@gmail.com")
    print("- Password: password123")
    print("\nOr use the test account:")
    print("- Email: test@example.com") 
    print("- Password: test123")

if __name__ == "__main__":
    setup_environment()
