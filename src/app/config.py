# app/config.py

import os 
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./saas.db")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
API_KEY_SECRET = os.getenv("API_KEY_SECRET", "your-api-secret-key")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  * 24 * 7   # 7 days
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days