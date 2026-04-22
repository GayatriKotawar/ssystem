from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel

from auth import hash_password, check_password
from database import get_user_by_email, create_user, save_document, get_user_documents, init_db

app = FastAPI(title="SmartDMS API")


@app.on_event("startup")
def startup():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
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

class UploadDocRequest:
    # FastAPI handles UploadFile seamlessly without BaseModel
    pass

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...), user_id: int = Form(...)):
    from workflow import process_upload

    # process_upload expects a file-like object with a .getvalue() method and .name
    # FastAPI UploadFile has `.file` which is a SpooledTemporaryFile
    # We can create a mock struct returning the bytes
    class MockFile:
        def __init__(self, filename, content):
            self.name = filename
            self.content = content
        def getvalue(self):
            return self.content

    content = await file.read()
    mock_file = MockFile(file.filename, content)
    
    try:
        results = process_upload(mock_file, user_id)
        if "error" in results:
            raise HTTPException(status_code=400, detail=results["error"])
        return results
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
