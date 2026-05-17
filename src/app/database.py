# app/databasse.py

from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os

# Database Connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./saas.db")

# Create Database Engine
engine = create_engine(
    DATABASE_URL,
    echo=True, # Set to False in production.
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create Database Tables
def create_db_and_tables():
    # Create Database Tables
    SQLModel.metadata.create_all(engine)
    
def get_session() -> Generator[Session, None, None]:
    # Database Session Dependency
    with Session(engine) as session:
        yield session