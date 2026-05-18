# app/auth.py

import bcrypt
import hmac
import hashlib
import secrets

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from app.models import User, ApiKey
from app.database import get_session
from app.config import SECRET_KEY, API_KEY_SECRET, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

security = HTTPBearer()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # Create JWT access token
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes = REFRESH_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    # Verify token and return email
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        email: str = payload.get("sub")
        token_type_from_payload: str = payload.get("type")
        if email is None or token_type_from_payload != token_type:
            return None
        return email
    except JWTError:
        return None
    
def generate_api_key() -> str:
    random_part = secrets.token_urlsafe(24)
    return f"sk_live_{random_part}"

def hash_api_key(api_key: str) -> str:
    return hmac.new(
        API_KEY_SECRET.encode('utf-8'),
        api_key.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
def verify_api_key(api_key: str, stored_hash: str) -> bool:
    computed_hash = hash_api_key(api_key)
    return hmac.compare_digest(computed_hash, stored_hash)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    # Get current userfrom JWT token
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"},
    )
    email = verify_token(credentials = credentials)
    
    if email is None: 
        raise credentials_exception
    
    statement = select(User).where(User.email == email)
    
    user = session.exec(statement).first()
    
    if user is None:
        raise credentials_exception
    
    return user

async def get_user_from_api_key(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: Session = Depends(get_session)
) -> tuple[User, ApiKey]:
    # Get current user from API key
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"},
    )
    
    api_key = credentials.credentials
    
    if not api_key.startswith("sk_live_"):
        raise credentials_exception
    
    api_key_hash = hash_api_key(api_key)
    
    statement = select(ApiKey).where(
        ApiKey.key_hash == api_key_hash,
        ApiKey.is_active == True
    )
    
    db_api_key = session.exec(statement).first()
    
    if db_api_key is None:
        raise credentials_exception
    
    statement = select(User).where(User.id == db_api_key.user_id)
    user = session.exec(statement).first()
    
    if user is None:
        raise credentials_exception
    
    return user, db_api_key