from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import os

# Security
security = HTTPBearer()
DEFAULT_API_KEY = os.environ.get("DEFAULT_API_KEY", "MookieWilson")

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify API key authentication"""
    if credentials.credentials != DEFAULT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials

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

@app.get("/members")
async def list_members(api_key: str = Depends(verify_api_key)):
    """Get list of all members"""
    return {"members": [], "message": "Database not yet configured with tables"}

@app.get("/members/{member_id}")
async def get_member_detail(member_id: str, api_key: str = Depends(verify_api_key)):
    """Get detailed member information"""
    return {
        "member": {
            "id": member_id,
            "message": "Database not yet configured"
        },
        "assessments": [],
        "assessment_count": 0
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("simple_main:app", host="0.0.0.0", port=port)