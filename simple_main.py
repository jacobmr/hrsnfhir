from fastapi import FastAPI, HTTPException
from datetime import datetime
import os

app = FastAPI(
    title="HRSN FHIR Processing Server",
    description="NY State 1115 Waiver HRSN Data Processing API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HRSN FHIR Processing Server",
        "version": "1.0.1",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "database_url": os.environ.get("DATABASE_URL", "not_set")[:50] + "..." if os.environ.get("DATABASE_URL") else "not_set"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "checking...",
        "version": "1.0.0",
        "environment": {
            "port": os.environ.get("PORT", "8000"),
            "database_url_set": bool(os.environ.get("DATABASE_URL")),
            "default_api_key": os.environ.get("DEFAULT_API_KEY", "MookieWilson")
        }
    }

@app.get("/members/count")
async def get_members_count():
    """Get count of members (simplified for testing)"""
    return {"members_count": 0, "status": "success", "message": "Database not connected yet"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("simple_main:app", host="0.0.0.0", port=port)