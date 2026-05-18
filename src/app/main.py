# app/main.py

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from datetime import timedelta
from typing import List
from app.database import create_db_and_tables, get_session
from contextlib import asynccontextmanager
from app.models import (
    User, ApiKey, UsageEvent,
    UserCreate, UserLogin, UserResponse,
    ApiKeyCreate, ApiKeyResponse, ApiKeyCreateResponse
)
from app.auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    generate_api_key, hash_api_key, verify_token,
    get_user_from_api_key, get_user_from_api_key
)

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    create_db_and_tables()
    yield
    # Clean up the ML models and release the resources
    # Run cleanup
    
app = FastAPI( 
    title="Story Generation SaaS API",
    description="AI-powered story generation with credit system",
    version="1.0.0"
    lifespan = lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"], 
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def root():
    return {"message": "Story Generation SaaS API"}

@app.get("/health")
def health_check():
    return{"status": "healthy", "service": "story-generation-api"}

@app.post("/auth/signup", response_model = UserResponse)
def signup(user_data: UserCreate, session: Session = Depends(get_session)):
    # User registration endpoint
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()
    
    if existing_user:
         raise HTTPException(
             status_code = status.HTTP_400_BAD_REQUEST,
             detail = "Email address already registered"
         )
    
    # Create a new user
    hashed_password = hash_password(user_data.password)
    user = User(
        email = user_data.email,
        password_hash = hashed_password,
        credits = 10, # Free credits for new users
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return UserResponse(
        id = user.id,
        email = user.id,
        credits = user.credits,
        created_at = user.created_at
    )

# Run and test.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)