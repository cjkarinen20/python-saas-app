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