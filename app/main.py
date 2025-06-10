# app/main.py
from fastapi import FastAPI, HTTPException, Depends, Security, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import logging
import os
from datetime import datetime
import uuid

from .database import get_db, engine
from .models import Base
from .fhir_processor import FHIRBundleProcessor
from .schemas import BundleResponse, HealthResponse, BundleProcessingStatus
from .config import settings

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
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

@app.get("/screening/{patient_id}")
async def get_patient_screenings(
    patient_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get screening history for a patient"""
    from .analytics import get_patient_screenings
    screenings = get_patient_screenings(db, patient_id)
    return {"patient_id": patient_id, "screenings": screenings}

@app.get("/eligibility/{patient_id}")
async def get_patient_eligibility(
    patient_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get eligibility assessments for a patient"""
    from .analytics import get_patient_eligibility_assessments
    assessments = get_patient_eligibility_assessments(db, patient_id)
    return {"patient_id": patient_id, "eligibility_assessments": assessments}

@app.get("/referrals/{patient_id}")
async def get_patient_referrals(
    patient_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get referral history for a patient"""
    from .analytics import get_patient_referrals
    referrals = get_patient_referrals(db, patient_id)
    return {"patient_id": patient_id, "referrals": referrals}

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