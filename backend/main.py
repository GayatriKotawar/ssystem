from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional, List
from pydantic import BaseModel

from auth import hash_password, check_password
from database import get_user_by_email, create_user, save_document, get_user_documents, init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (nothing needed)

app = FastAPI(title="SmartDMS API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserAuthMode(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

@app.get("/")
def read_root():
    return {"status": "ok", "message": "SmartDMS API is running"}

@app.post("/api/auth/signup")
def signup(user: UserAuthMode):
    if not user.name:
        raise HTTPException(status_code=400, detail="Name is required for signup")
        
    hashed = hash_password(user.password)
    success = create_user(user.name, user.email, hashed)
    if not success:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    return {"message": "User created successfully"}

@app.post("/api/auth/login")
def login(user: UserAuthMode):
    db_user = get_user_by_email(user.email)
    if not db_user or not check_password(user.password, db_user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    # In a real app we would issue a JWT here. For simplicity in this rewrite,
    # we'll return user details (minus password) to be stored in React state/context
    user_data = dict(db_user)
    del user_data['password_hash']
    return user_data

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...), user_id: int = Form(...)):
    import asyncio
    from functools import partial
    from workflow import process_upload

    # Read file bytes asynchronously
    content = await file.read()
    filename = file.filename

    # Run the CPU/IO-bound processing in a thread pool so the event loop stays free
    class _FileAdapter:
        """Thin adapter so workflow.py's process_upload can call .getvalue() and .name."""
        def __init__(self, name, data):
            self.name = name
            self._data = data
        def getvalue(self):
            return self._data

    adapter = _FileAdapter(filename, content)
    loop = asyncio.get_event_loop()

    try:
        results = await loop.run_in_executor(None, partial(process_upload, adapter, user_id))
        # Only treat "error" as a hard failure if there's nothing else useful returned
        if results.get("error") and len(results) <= 2:
            raise HTTPException(status_code=400, detail=results["error"])
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/{user_id}")
def get_documents(user_id: int):
    df = get_user_documents(user_id)
    # Convert DataFrame to list of dicts
    docs = df.to_dict(orient="records")
    return {"documents": docs}

@app.get("/api/alerts/{user_id}")
def get_alerts(user_id: int):
    from utils.alerts import get_user_alerts

    alerts = get_user_alerts(user_id)
    return {"alerts": alerts}
