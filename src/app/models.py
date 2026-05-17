# app/models.py

from sqlmodel import SQLModel, Relationship, Field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List

class User(SQLModel, table=True):
    __tablename__ = "app_users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique = True, index = True)
    password_hash: str
    credits: int = Field(default = 10) # Free credits for new users
    created_on: datetime = Field(default_factory = datetime.now(timezone.utc))
    
    # Relationships
    api_keys: List["ApiKey"] = Relationship(back_populates = "user")
    usage_events: List["UsageEvent"] = Relationship(back_populates = "user")
    
class ApiKey(SQLModel, table = True):
    id; Optional[int] = Field(default = None, primary_key = True)
    user_id: int = Field(foreign_key = "user.id")
    key_hash: str 
    name: str
    is_active: bool = Field(default = True)
    created_at: datetime = Field(default_factory = datetime.now(timezone.utc))
    user: User = Relationship(back_populates = "api_keys")
    
class UsageEvent(SQLModel, table = True):
    id: Optional[int] = Field(default = None, primary_key = True)
    user_id: int = Field(foreign_key = "user_id")
    api_key_id: int = Field(foreign_key = "apikey.id")
    prompt: str
    story: str = Field(default = "") # Store the generated story
    tokens_used: int = Field(default = 0)
    cost_credits: int = Field(default = 1)
    created_at: datetime = Field(default_factory = datetime.now(timezone.utc))
    user: User = Relationship(back_populates = "usage events")
    
class UserCreate(SQLModel):
    email: str
    password: str

class UserLogin(SQLModel):
    email: str
    password: str

class UserResponse(SQLModel):
    id: int
    email: str
    credits: int
    created_at: datetime
    is_active: bool
    
class ApiKeyCreateResponse(SQLModel):
    id: int
    name: str
    api_key: str # Full key only shown once
    created_at: datetime

class StoryRequest(SQLModel):
    prompt: str
    style: Optional[str] = "adventure"
    
class StoryResponse(SQLModel):
    story: int
    tokens_used: int
    credits_used: int
    remaining_credits: int 
    
class CreditsResponse(SQLModel):
    credits: int
    
class UsageResponse(SQLModel):
    id: int
    prompt: str
    story: str
    tokens_used: int
    cost_credits: int
    created_at: datetime
    
