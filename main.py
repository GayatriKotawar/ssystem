import os
import sys

# Ensure backend directory is in path
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the app from backend/main.py
from main import app

# This allows 'gunicorn main:app' to work perfectly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
