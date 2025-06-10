# app/main.py
from fastapi import FastAPI, HTTPException, Depends, Security, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import logging
import os
from datetime import datetime, date
import uuid

from .database import get_db, engine
from .models import Base
from .fhir_processor import FHIRBundleProcessor
from .schemas import BundleResponse, HealthResponse, BundleProcessingStatus
from .config import settings
import sys
import os

# Use production settings if in Azure
if 'WEBSITE_HOSTNAME' in os.environ:
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from app_config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="HRSN FHIR Processing Server",
    description="NY State 1115 Waiver HRSN Data Processing API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
allowed_origins = ["*"]  # Default for development
if hasattr(settings, 'ALLOWED_ORIGINS'):
    allowed_origins = settings.ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify API key authentication"""
    if credentials.credentials != settings.DEFAULT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials

# Initialize FHIR processor
fhir_processor = FHIRBundleProcessor()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" else "unhealthy",
        timestamp=datetime.utcnow(),
        database=db_status,
        version="1.0.0"
    )

@app.post("/fhir/Bundle", response_model=BundleResponse)
async def receive_fhir_bundle(
    bundle: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Receive and process FHIR Bundle containing HRSN screening data
    
    Validates the bundle structure and queues it for processing
    """
    try:
        # Generate processing ID
        processing_id = str(uuid.uuid4())
        
        # Basic validation
        if not isinstance(bundle, dict) or bundle.get("resourceType") != "Bundle":
            raise HTTPException(status_code=400, detail="Invalid FHIR Bundle structure")
        
        bundle_id = bundle.get("id")
        if not bundle_id:
            raise HTTPException(status_code=400, detail="Bundle must have an ID")
        
        logger.info(f"Received FHIR Bundle {bundle_id} for processing {processing_id}")
        
        # Queue for background processing
        background_tasks.add_task(
            process_bundle_async, 
            bundle, 
            processing_id, 
            db_session_maker=get_db
        )
        
        return BundleResponse(
            bundle_id=bundle_id,
            processing_id=processing_id,
            status="accepted",
            message="Bundle queued for processing",
            received_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error receiving bundle: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def process_bundle_async(bundle: Dict[str, Any], processing_id: str, db_session_maker):
    """Background task to process FHIR bundle"""
    db = next(db_session_maker())
    try:
        logger.info(f"Starting background processing for {processing_id}")
        result = await fhir_processor.process_bundle(bundle, db)
        logger.info(f"Completed processing {processing_id}: {result}")
    except Exception as e:
        logger.error(f"Background processing failed for {processing_id}: {e}")
    finally:
        db.close()

@app.get("/fhir/Bundle/{bundle_id}")
async def get_bundle_status(
    bundle_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get processing status for a specific bundle"""
    # Implementation would track processing status
    # For now, return basic info
    return {"bundle_id": bundle_id, "status": "processed"}

@app.get("/screening/{member_id}")
async def get_member_screenings(
    member_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get screening history for a member"""
    from .analytics import get_member_screenings
    screenings = get_member_screenings(db, member_id)
    return {"member_id": member_id, "screenings": screenings}

@app.get("/eligibility/{member_id}")
async def get_member_eligibility(
    member_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get eligibility assessments for a member"""
    from .analytics import get_member_eligibility_assessments
    assessments = get_member_eligibility_assessments(db, member_id)
    return {"member_id": member_id, "eligibility_assessments": assessments}

@app.get("/referrals/{member_id}")
async def get_member_referrals(
    member_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get referral history for a member"""
    from .analytics import get_member_referrals
    referrals = get_member_referrals(db, member_id)
    return {"member_id": member_id, "referrals": referrals}

def calculate_age(birth_date: datetime) -> Optional[int]:
    """Calculate age from birth date"""
    if not birth_date:
        return None
    
    today = date.today()
    birth_date_only = birth_date.date() if isinstance(birth_date, datetime) else birth_date
    
    age = today.year - birth_date_only.year - (
        (today.month, today.day) < (birth_date_only.month, birth_date_only.day)
    )
    return age

@app.get("/members")
async def get_members_list(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get list of all members with basic info for members page"""
    from .models import Member
    
    members = db.query(Member).all()
    
    members_list = []
    for member in members:
        age = calculate_age(member.date_of_birth) if member.date_of_birth else None
        
        members_list.append({
            "id": str(member.id),
            "fhir_id": member.fhir_id,
            "full_name": f"{member.first_name or ''} {member.last_name or ''}".strip(),
            "first_name": member.first_name,
            "last_name": member.last_name,
            "age": age,
            "zip_code": member.zip_code,
            "date_of_birth": member.date_of_birth.isoformat() if member.date_of_birth else None,
            "created_at": member.created_at.isoformat() if member.created_at else None
        })
    
    # Sort by last name, then first name
    members_list.sort(key=lambda x: (x["last_name"] or "", x["first_name"] or ""))
    
    return {
        "members": members_list,
        "total_count": len(members_list)
    }

@app.get("/members/{member_id}")
async def get_member_detail(
    member_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get detailed information for a specific member including all assessments"""
    from .models import Member
    from .analytics import get_member_screenings, get_member_eligibility_assessments, get_member_referrals
    
    # Find member by either UUID or FHIR ID
    member = db.query(Member).filter(
        (Member.id == member_id) | (Member.fhir_id == member_id)
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Get age
    age = calculate_age(member.date_of_birth) if member.date_of_birth else None
    
    # Get all assessments
    screenings = get_member_screenings(db, member.fhir_id)
    eligibility_assessments = get_member_eligibility_assessments(db, member.fhir_id)
    referrals = get_member_referrals(db, member.fhir_id)
    
    return {
        "member": {
            "id": str(member.id),
            "fhir_id": member.fhir_id,
            "mrn": member.mrn,
            "full_name": f"{member.first_name or ''} {member.last_name or ''}".strip(),
            "first_name": member.first_name,
            "last_name": member.last_name,
            "age": age,
            "date_of_birth": member.date_of_birth.isoformat() if member.date_of_birth else None,
            "gender": member.gender,
            "address_line1": member.address_line1,
            "city": member.city,
            "state": member.state,
            "zip_code": member.zip_code,
            "created_at": member.created_at.isoformat() if member.created_at else None
        },
        "assessments": {
            "screenings": screenings,
            "eligibility_assessments": eligibility_assessments,
            "referrals": referrals
        },
        "summary": {
            "total_screenings": len(screenings),
            "total_eligibility_assessments": len(eligibility_assessments),
            "total_referrals": len(referrals),
            "latest_screening_date": screenings[0].screening_date.isoformat() if screenings else None
        }
    }

@app.get("/analytics/dashboard")
async def get_dashboard_analytics(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get dashboard analytics for HRSN data"""
    from .analytics import generate_dashboard_data
    
    data = generate_dashboard_data(db)
    return data

@app.get("/reports/safety-scores")
async def get_safety_score_report(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Generate safety score analysis report"""
    from .analytics import analyze_safety_scores
    
    report = analyze_safety_scores(db)
    return report

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )