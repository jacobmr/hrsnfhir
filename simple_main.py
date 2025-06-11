from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, text, Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from datetime import datetime, date
import os
import uuid

# Database setup
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = None
SessionLocal = None
Base = declarative_base()

# Database Models
class Member(Base):
    __tablename__ = "members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fhir_id = Column(String(64), unique=True, nullable=False)
    mrn = Column(String(50))
    first_name = Column(String(100))
    last_name = Column(String(100))
    date_of_birth = Column(DateTime)
    gender = Column(String(20))
    address = Column(String(500))
    address_line1 = Column(String(200))
    city = Column(String(100))
    state = Column(String(2))
    zip_code = Column(String(10))
    phone = Column(String(20))
    created_at = Column(DateTime, default=func.now())

class ScreeningSession(Base):
    __tablename__ = "screening_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    bundle_id = Column(String(64))
    fhir_questionnaire_response_id = Column(String(64))
    screening_date = Column(DateTime)
    consent_given = Column(Boolean)
    screening_complete = Column(Boolean)
    total_safety_score = Column(Integer)
    positive_screens_count = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

# Database connection
if DATABASE_URL and DATABASE_URL != "Postgres.DATABASE_URL":
    try:
        # Fix postgres:// to postgresql:// if needed
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
        engine = create_engine(DATABASE_URL, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
        
    except Exception as e:
        print(f"Database connection error: {e}")
        engine = None
        SessionLocal = None

def get_db():
    """Database dependency"""
    if SessionLocal:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    else:
        yield None

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

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    try:
        with open("app/static/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to API response if HTML file not found
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head><title>HRSN FHIR Processing Server</title></head>
        <body>
            <h1>HRSN FHIR Processing Server</h1>
            <p>Status: Running</p>
            <p><a href="/docs">API Documentation</a></p>
            <p><a href="/health">Health Check</a></p>
        </body>
        </html>
        """)

@app.get("/api")
async def api_root():
    """API endpoint for programmatic access"""
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
    db_status = "not_configured"
    db_url = os.environ.get("DATABASE_URL", "")
    
    if not db_url:
        db_status = "no_database_url"
    elif db_url == "Postgres.DATABASE_URL":
        db_status = "template_variable_not_replaced"
    elif engine:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_status = "connected"
        except Exception as e:
            db_status = f"connection_error: {str(e)[:100]}"
    else:
        db_status = "engine_creation_failed"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "version": "1.0.3",
        "environment": {
            "port": os.environ.get("PORT", "8000"),
            "database_url_set": bool(db_url),
            "database_url_preview": db_url[:100] + "..." if db_url and len(db_url) > 100 else db_url,
            "default_api_key": DEFAULT_API_KEY,
            "tables_created": engine is not None,
            "all_env_vars": [k for k in os.environ.keys() if "DATA" in k.upper() or "POST" in k.upper()]
        }
    }

@app.get("/members/count")
async def get_members_count():
    """Get count of members"""
    if not engine:
        return {"members_count": 0, "status": "error", "message": "Database not configured"}
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM members"))
            count = result.scalar()
        return {"members_count": count, "status": "success"}
    except Exception as e:
        return {"members_count": 0, "status": "error", "message": f"Database error: {str(e)[:100]}"}

@app.get("/members")
async def list_members(db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Get list of all members"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        members = db.query(Member).limit(100).all()
        
        member_list = []
        for member in members:
            age = None
            if member.date_of_birth:
                today = date.today()
                birth_date = member.date_of_birth.date() if hasattr(member.date_of_birth, 'date') else member.date_of_birth
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            zip_code = ""
            if member.zip_code:
                zip_code = member.zip_code
            elif member.address:
                import re
                zip_match = re.search(r'\b\d{5}(?:-\d{4})?\b', member.address)
                if zip_match:
                    zip_code = zip_match.group()
            
            member_list.append({
                "id": str(member.id),
                "name": f"{member.first_name or ''} {member.last_name or ''}".strip(),
                "age": age,
                "zip_code": zip_code
            })
        
        return {"members": member_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/members/{member_id}")
async def get_member_detail(member_id: str, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Get detailed member information with assessments"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        member = db.query(Member).filter(Member.id == member_id).first()
        
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        # Calculate age
        age = None
        if member.date_of_birth:
            today = date.today()
            birth_date = member.date_of_birth.date() if hasattr(member.date_of_birth, 'date') else member.date_of_birth
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        # Get zip code
        zip_code = ""
        if member.zip_code:
            zip_code = member.zip_code
        elif member.address:
            import re
            zip_match = re.search(r'\b\d{5}(?:-\d{4})?\b', member.address)
            if zip_match:
                zip_code = zip_match.group()
        
        # Get all screenings for this member
        screenings = db.query(ScreeningSession).filter(ScreeningSession.member_id == member.id).all()
        
        assessments = []
        for screening in screenings:
            assessments.append({
                "id": str(screening.id),
                "screening_date": screening.screening_date.isoformat() if screening.screening_date else None,
                "total_safety_score": screening.total_safety_score,
                "questions_answered": screening.questions_answered,
                "positive_screens": screening.positive_screens_count,
                "high_risk": screening.total_safety_score >= 11 if screening.total_safety_score else False
            })
        
        return {
            "member": {
                "id": str(member.id),
                "name": f"{member.first_name or ''} {member.last_name or ''}".strip(),
                "first_name": member.first_name,
                "last_name": member.last_name,
                "age": age,
                "date_of_birth": member.date_of_birth.isoformat() if member.date_of_birth else None,
                "gender": member.gender,
                "address": member.address,
                "zip_code": zip_code,
                "phone": member.phone,
                "mrn": member.mrn
            },
            "assessments": assessments,
            "assessment_count": len(assessments)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("simple_main:app", host="0.0.0.0", port=port)