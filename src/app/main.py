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
    ApiKeyCreate, ApiKeyResponse, ApiKeyCreateResponse,
    StoryRequest, StoryResponse, CreditsResponse,
    UsageResponse
)
from app.auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    generate_api_key, hash_api_key, verify_token,
    get_current_user, get_user_from_api_key
)

from app.services import (
    CreditService, StoryGenerationService
)
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from app import stripe_routes


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
    version="1.0.0",
    lifespan = lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"], 
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

app.include_router(stripe_routes.router)

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
        created_on = user.created_on
    )

@app.post("/auth/signup", response_model = UserResponse)
def login(user_data: UserLogin, session: Session = Depends(get_session)):
    # User login endpoint - returns access and refresh tokens
    statement = select(User).where(User.email == user_data.email)
    user = session.exec(statement).first()
    
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect email or password"
        )

    # Create tokens
    access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data = {"sub": user.email}, expires_delta = access_token_expires
    )

    refresh_token_expires = timedelta(minutes = REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        data = {"sub": user.email}, expires_delta = refresh_token_expires
    )

    return {
        "access token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse(
            id = user.id,
            email = user.email,
            credits = user.credits,
            created_on = user.created_on
        )
    }

@app.post("/auth/refresh")
def refresh_token_endpoint(request: dict, session: Session = Depends(get_session)):
    # Refresh access token using refresh token
    
    refresh_token = request.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Refresh token is required."
        )
    
    email = verify_token(refresh_token, "refresh")
    
    if email is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid refresh token"
        )
    
    access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data = {"sub": email}, expires_delta = access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
    
@app.post("/api-keys", response_model = ApiKeyCreateResponse)
def create_api_key(
    api_key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
        # Create new API key for authenticated user
        api_key = generate_api_key()
        key_hash = hash_api_key(api_key)
        
        # Store in DB
        db_api_key = ApiKey(
            user_id = current_user.id,
            key_hash = key_hash,
            name = api_key_data.name
        )
        
        session.add(db_api_key)
        session.commit()
        session.refresh(db_api_key)
        
        # Return the actual key
        return ApiKeyCreateResponse(
            id = db_api_key.id,
            name = db_api_key.name,
            api_key = api_key,
            created_on = db_api_key.created_on
        )
        
@app.get("/api-keys", response_model = List[ApiKeyResponse])
def list_api_keys(
    current_user: User= Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # List user's API keys
    statement = select(ApiKey).where(
        ApiKey.user_id == current_user.id,
        ApiKey.is_active == True
    )
        
    api_keys = session.exec(statement).all()
    
    return [
        ApiKeyResponse(
            id = key.id,
            name = key.name,
            key_has = key.key_hash[:8] + "...", # Truncated for security
            created_on = key.created_on,
            is_active = key.is_active
            
        )
        for key in api_keys
    ]
        
        
@app.delete("/api-keys/{key_id}")
def deactivate_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    
    # Deactivate API Key (soft delete)
    statement = select(ApiKey).where(
        ApiKey.id == key_id.id,
        ApiKey.user_id == current_user.id
    )
    
    api_key = session.exec(statement).first()
    
    if not api_key:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "API key not found."
        )
    
    api_key.is_active = False
    session.add(api_key)
    session.commit()
    
    return {"message": "API key successfully deactivated."}

@app.get("/auth/me", response_model = UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id = current_user.id, # type: ignore
        email = current_user.email,
        credits = current_user.credits, 
        created_on = current_user.created_on
    )

@app.post("/v1/story/generate", response_model = StoryResponse)
def generate_story(
    story_request: StoryRequest,
    user_and_key: tuple[User, ApiKey] = Depends(get_user_from_api_key),
    session: Session = Depends(get_session)
):
    # Generate story endpoint - requires API key authentication
    user, api_key = user_and_key

    # Check and deduct credits
    if not CreditService.deduct_credits(session, user, 1):
        raise HTTPException(
            status_code = status.HTTP_402_PAYMENT_REQUIRED,
            detail = "Insufficient Credits"
        )
    
    try:
        # Generate story
        result = StoryGenerationService.generate_story(
            story_request.prompt,
            story_request.style or "adventure"
        )
        
        StoryGenerationService.log_usage(
            session = session,
            user = user,
            api_key = api_key,
            prompt = story_request.prompt,
            story = result["story"],
            tokens_used = result["tokens_used"],
            cost_credits = 1
        )

        # Refresh user to get updated credits
        session.refresh(user)
        
        return StoryResponse(
            story = result["story"],
            tokens_used = result["tokens_used"],
            credits_used = 1,
            remaining_credits = user.credits
        )
        
    except Exception as e:
        # Refund credits if generation fails
        CreditService.refund_credits(session, user, 1)
        raise e 

@app.get("/v1/me/credits", response_model = CreditsResponse)
def get_credits(user_and_key: tuple[User, ApiKey] = Depends(get_user_from_api_key)):
    # Get user's credit balance
    user, _ = user_and_key
    
    return CreditsResponse(credits = user.credits)

@app.get("/v1/me/usage", response_model = List[UsageResponse])
def get_usage(
    skip: int = Query(0, ge = 0),
    limit: int = Query(10, ge = 1, le = 100),
    user_and_key: tuple[User, ApiKey] = Depends(get_user_from_api_key),
    session: Session = Depends(get_session)  
):

    # Get usage history for API key authentication
    user, _ = user_and_key
    
    statement = select(UsageEvent).where(
        UsageEvent.user_id == user.id
    ).order_by(UsageEvent.created_on.desc()).offset(skip).limit(limit) # Type: ignore
    
    usage_events = session.exec(statement).all()
    
    return [
        UsageResponse(
            id = event.id, # Type: ignore
            prompt = event.prompt,
            story = event.story,
            tokens_used = event.tokens_used, 
            cost_credits = event.cost_credits,
            created_on = event.created_on
        )
        for event in usage_events
    ]


# Run and test.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "0.0.0.0", port = 8000)