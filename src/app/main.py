# app/main.py

from fastapi import FastAPI
from app.database import create_db_and_tables
from contextlib import asynccontextmanager

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

app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def root():
    return {"message": "Story Generation SaaS API"}

@app.get("/health")
def health_check():
    return{"status": "healthy", "service": "story-generation-api"}

# Run and test.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)