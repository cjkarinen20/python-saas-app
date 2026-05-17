# app/main.py

from fastapi import FastAPI

app = FastAPI( 
    title="Story Generation SaaS API",
    description="AI-powered story generation with credit system",
    version="1.0.0"
)

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