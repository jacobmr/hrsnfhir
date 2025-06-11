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
import logging
import re

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

class ScreeningResponse(Base):
    __tablename__ = "screening_responses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    screening_session_id = Column(UUID(as_uuid=True), ForeignKey("screening_sessions.id"), nullable=False)
    question_code = Column(String(20))
    question_text = Column(String(500))
    answer_code = Column(String(20))
    answer_text = Column(String(200))
    sdoh_category = Column(String(50))
    positive_screen = Column(Boolean)
    data_absent_reason = Column(String(50))
    created_at = Column(DateTime, default=func.now())

# HRSN Question Mappings - simplified version
HRSN_QUESTION_MAPPINGS = {
    # Safety Questions 9-12 (for scoring)
    "95618-5": {
        "text": "How often does anyone, including family and friends, physically hurt you",
        "category": ["sdoh-category-unspecified"],
        "safety_question": True,
        "score_mapping": {
            "LA6270-8": 1,    # Never
            "LA10066-1": 2,   # Rarely
            "LA10082-8": 3,   # Sometimes
            "LA16644-9": 4,   # Fairly often
            "LA6482-9": 5     # Frequently
        }
    },
    "95617-7": {
        "text": "How often does anyone, including family and friends, insult or talk down to you",
        "category": ["sdoh-category-unspecified"],
        "safety_question": True,
        "score_mapping": {
            "LA6270-8": 1,    # Never
            "LA10066-1": 2,   # Rarely
            "LA10082-8": 3,   # Sometimes
            "LA16644-9": 4,   # Fairly often
            "LA6482-9": 5     # Frequently
        }
    },
    "95616-9": {
        "text": "How often does anyone, including family and friends, threaten you with harm",
        "category": ["sdoh-category-unspecified"],
        "safety_question": True,
        "score_mapping": {
            "LA6270-8": 1,    # Never
            "LA10066-1": 2,   # Rarely
            "LA10082-8": 3,   # Sometimes
            "LA16644-9": 4,   # Fairly often
            "LA6482-9": 5     # Frequently
        }
    },
    "95615-1": {
        "text": "How often does anyone, including family and friends, scream or curse at you",
        "category": ["sdoh-category-unspecified"],
        "safety_question": True,
        "score_mapping": {
            "LA6270-8": 1,    # Never
            "LA10066-1": 2,   # Rarely
            "LA10082-8": 3,   # Sometimes
            "LA16644-9": 4,   # Fairly often
            "LA6482-9": 5     # Frequently
        }
    },
    # Food insecurity questions
    "88122-7": {
        "text": "Within the past 12 months, you worried that your food would run out before you got money to buy more",
        "category": ["food-insecurity"],
        "positive_answers": ["LA28397-0", "LA6729-3"]  # Often true, Sometimes true
    },
    "88123-5": {
        "text": "Within the past 12 months, the food you bought just didn't last and you didn't have money to get more",
        "category": ["food-insecurity"],
        "positive_answers": ["LA28397-0", "LA6729-3"]  # Often true, Sometimes true
    },
    # Transportation
    "93030-5": {
        "text": "In the past 12 months, has lack of reliable transportation kept you from medical appointments, meetings, work or from getting things needed for daily living",
        "category": ["transportation-insecurity"],
        "positive_answers": ["LA33-6"]  # Yes
    }
}

class FHIRBundleProcessor:
    """Simple FHIR bundle processor for basic functionality"""
    
    def __init__(self):
        self.safety_questions = ["95618-5", "95617-7", "95616-9", "95615-1"]
    
    def process_bundle(self, bundle_dict: dict, db: Session) -> dict:
        """Main entry point for processing FHIR bundles"""
        try:
            logging.info(f"Processing FHIR bundle: {bundle_dict.get('id', 'unknown')}")
            
            # Basic validation
            if not isinstance(bundle_dict, dict) or bundle_dict.get("resourceType") != "Bundle":
                raise ValueError("Invalid FHIR Bundle structure")
            
            bundle_id = bundle_dict.get("id")
            entries = bundle_dict.get("entry", [])
            
            result = {
                "bundle_id": bundle_id,
                "members_processed": 0,
                "screenings_processed": 0,
                "status": "completed"
            }
            
            # Process each resource in the bundle
            for entry in entries:
                resource = entry.get("resource", {})
                resource_type = resource.get("resourceType")
                
                if resource_type == "Patient":
                    self._process_member(resource, db)
                    result["members_processed"] += 1
                elif resource_type == "QuestionnaireResponse":
                    self._process_questionnaire_response(resource, db)
                    result["screenings_processed"] += 1
            
            db.commit()
            logging.info(f"Successfully processed bundle {bundle_id}")
            return result
            
        except Exception as e:
            logging.error(f"Error processing bundle: {e}")
            db.rollback()
            raise
    
    def _process_member(self, patient_resource: dict, db: Session) -> Member:
        """Process a FHIR Patient resource into a Member"""
        fhir_id = patient_resource.get("id")
        if not fhir_id:
            raise ValueError("Patient resource missing ID")
        
        # Check for existing member
        existing_member = db.query(Member).filter(Member.fhir_id == fhir_id).first()
        if existing_member:
            return existing_member
        
        # Extract name
        name_data = patient_resource.get("name", [])
        first_name = ""
        last_name = ""
        if name_data and isinstance(name_data, list) and len(name_data) > 0:
            name = name_data[0]
            given = name.get("given", [])
            if given:
                first_name = " ".join(given) if isinstance(given, list) else str(given)
            last_name = name.get("family", "")
        
        # Extract other data
        gender = patient_resource.get("gender", "")
        birth_date_str = patient_resource.get("birthDate", "")
        birth_date = None
        if birth_date_str:
            try:
                birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
            except:
                pass
        
        # Extract address
        addresses = patient_resource.get("address", [])
        address_line1 = ""
        city = ""
        state = ""
        zip_code = ""
        address_full = ""
        if addresses and len(addresses) > 0:
            addr = addresses[0]
            lines = addr.get("line", [])
            if lines:
                address_line1 = lines[0] if isinstance(lines, list) else str(lines)
            city = addr.get("city", "")
            state = addr.get("state", "")
            zip_code = addr.get("postalCode", "")
            
            # Build full address
            parts = []
            if address_line1:
                parts.append(address_line1)
            if city:
                parts.append(city)
            if state:
                parts.append(state)
            if zip_code:
                parts.append(zip_code)
            address_full = ", ".join(parts)
        
        # Create new member
        member = Member(
            fhir_id=fhir_id,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=birth_date,
            gender=gender,
            address=address_full,
            address_line1=address_line1,
            city=city,
            state=state,
            zip_code=zip_code
        )
        
        db.add(member)
        db.flush()  # Get the ID
        return member
    
    def _process_questionnaire_response(self, qr_resource: dict, db: Session):
        """Process a QuestionnaireResponse into screening data"""
        session_id = qr_resource.get("id")
        if not session_id:
            return
        
        # Get member reference
        subject_ref = qr_resource.get("subject", {}).get("reference", "")
        if subject_ref.startswith("Patient/"):
            member_fhir_id = subject_ref.replace("Patient/", "")
            member = db.query(Member).filter(Member.fhir_id == member_fhir_id).first()
            if not member:
                logging.warning(f"Member not found for reference: {subject_ref}")
                return
        else:
            logging.warning(f"Invalid subject reference: {subject_ref}")
            return
        
        # Create screening session
        authored_date_str = qr_resource.get("authored", "")
        screening_date = datetime.utcnow()
        if authored_date_str:
            try:
                screening_date = datetime.fromisoformat(authored_date_str.replace("Z", "+00:00"))
            except:
                pass
        
        screening = ScreeningSession(
            member_id=member.id,
            screening_date=screening_date,
            fhir_questionnaire_response_id=session_id
        )
        
        db.add(screening)
        db.flush()  # Get the ID
        
        # Process responses
        safety_score = 0
        positive_screens = 0
        questions_answered = 0
        
        items = qr_resource.get("item", [])
        for item in items:
            question_code = item.get("linkId")
            question_text = item.get("text", "")
            
            if question_code and question_code in HRSN_QUESTION_MAPPINGS:
                questions_answered += 1
                
                for answer in item.get("answer", []):
                    answer_code = None
                    answer_text = ""
                    
                    if "valueCoding" in answer:
                        coding = answer["valueCoding"]
                        answer_code = coding.get("code")
                        answer_text = coding.get("display", answer_code or "")
                    elif "valueString" in answer:
                        answer_text = answer["valueString"]
                    elif "valueBoolean" in answer:
                        answer_text = "Yes" if answer["valueBoolean"] else "No"
                    elif "valueInteger" in answer:
                        answer_text = str(answer["valueInteger"])
                    
                    # Calculate safety score
                    if question_code in self.safety_questions and answer_code:
                        score_mapping = HRSN_QUESTION_MAPPINGS[question_code].get("score_mapping", {})
                        if answer_code in score_mapping:
                            safety_score += score_mapping[answer_code]
                    
                    # Check for positive screen
                    positive_answers = HRSN_QUESTION_MAPPINGS[question_code].get("positive_answers", [])
                    if answer_code in positive_answers:
                        positive_screens += 1
                    
                    # Create response record
                    response = ScreeningResponse(
                        screening_session_id=screening.id,
                        question_code=question_code,
                        question_text=question_text,
                        answer_code=answer_code,
                        answer_text=answer_text
                    )
                    db.add(response)
        
        # Update screening with calculated values
        screening.total_safety_score = safety_score
        screening.positive_screens_count = positive_screens
        screening.questions_answered = questions_answered

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
else:
    # Fallback: try the actual Railway PostgreSQL URL if the variable isn't set correctly
    try:
        fallback_url = "postgresql://postgres:wHmchslvFsGDCONyYLCeWXaWlaLWHWaI@ballast.proxy.rlwy.net:39256/railway"
        engine = create_engine(fallback_url, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("Database connected successfully using fallback URL")
        
    except Exception as e:
        print(f"Fallback database connection error: {e}")
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
        "version": "1.0.4",
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

@app.delete("/members/{member_id}")
async def delete_member(member_id: str, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Delete a member and all associated data"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Check if member exists
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        # Get member name for response
        member_name = f"{member.first_name or ''} {member.last_name or ''}".strip()
        if not member_name:
            member_name = f"Member {member_id[:8]}"
        
        # Delete screening responses first (due to foreign key constraints)
        screening_sessions = db.query(ScreeningSession).filter(ScreeningSession.member_id == member.id).all()
        for session in screening_sessions:
            db.query(ScreeningResponse).filter(ScreeningResponse.screening_session_id == session.id).delete()
        
        # Delete screening sessions
        db.query(ScreeningSession).filter(ScreeningSession.member_id == member.id).delete()
        
        # Delete the member
        db.delete(member)
        db.commit()
        
        return {
            "message": f"Member {member_name} deleted successfully",
            "deleted_member": {
                "id": str(member.id),
                "name": member_name
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/assessments/{assessment_id}")
async def get_assessment_detail(assessment_id: str, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Get detailed assessment information with all responses"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get screening session
        screening = db.query(ScreeningSession).filter(ScreeningSession.id == assessment_id).first()
        if not screening:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Get member info
        member = db.query(Member).filter(Member.id == screening.member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found for this assessment")
        
        # Get all responses for this screening
        responses = db.query(ScreeningResponse).filter(ScreeningResponse.screening_session_id == screening.id).all()
        
        # Calculate age
        age = None
        if member.date_of_birth:
            from datetime import date
            today = date.today()
            birth_date = member.date_of_birth.date() if hasattr(member.date_of_birth, 'date') else member.date_of_birth
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        # Organize responses by category
        responses_by_category = {}
        for response in responses:
            category = response.sdoh_category or "general"
            if category not in responses_by_category:
                responses_by_category[category] = []
            
            responses_by_category[category].append({
                "question_code": response.question_code,
                "question_text": response.question_text,
                "answer_code": response.answer_code,
                "answer_text": response.answer_text,
                "positive_screen": response.positive_screen,
                "is_safety_question": response.question_code in ["95618-5", "95617-7", "95616-9", "95615-1"]
            })
        
        return {
            "assessment": {
                "id": str(screening.id),
                "screening_date": screening.screening_date.isoformat() if screening.screening_date else None,
                "total_safety_score": screening.total_safety_score,
                "questions_answered": screening.questions_answered,
                "positive_screens_count": screening.positive_screens_count,
                "high_risk": screening.total_safety_score >= 11 if screening.total_safety_score else False,
                "consent_given": screening.consent_given,
                "screening_complete": screening.screening_complete,
                "bundle_id": screening.bundle_id,
                "fhir_questionnaire_response_id": screening.fhir_questionnaire_response_id
            },
            "member": {
                "id": str(member.id),
                "name": f"{member.first_name or ''} {member.last_name or ''}".strip(),
                "first_name": member.first_name,
                "last_name": member.last_name,
                "age": age,
                "date_of_birth": member.date_of_birth.isoformat() if member.date_of_birth else None,
                "gender": member.gender,
                "address": member.address,
                "zip_code": member.zip_code,
                "phone": member.phone,
                "mrn": member.mrn
            },
            "responses": responses_by_category,
            "response_count": len(responses)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/debug/env")
async def debug_env(api_key: str = Depends(verify_api_key)):
    """Debug endpoint to see environment variables"""
    env_vars = {}
    # Show all environment variables that might be related to database
    for key, value in os.environ.items():
        if any(keyword in key.upper() for keyword in ["DATABASE", "POSTGRES", "DB", "SQL", "PG"]):
            # Mask sensitive parts but show structure
            if "URL" in key.upper() and "://" in value:
                parts = value.split("://")
                if len(parts) > 1:
                    env_vars[key] = f"{parts[0]}://***masked***"
                else:
                    env_vars[key] = "***masked***"
            else:
                env_vars[key] = value[:50] + "..." if len(str(value)) > 50 else value
    
    # Also show Railway-specific variables
    railway_vars = {}
    for key, value in os.environ.items():
        if key.startswith("RAILWAY") or "SERVICE" in key.upper():
            railway_vars[key] = value[:50] + "..." if len(str(value)) > 50 else value
    
    return {
        "database_env_vars": env_vars,
        "railway_vars": railway_vars,
        "DATABASE_URL": os.environ.get("DATABASE_URL", "NOT_SET"),
        "total_env_vars": len(os.environ)
    }

# Original extraction functions for web interface compatibility
def extract_bundle_data(bundle: dict) -> dict:
    """Extract data from FHIR bundle and organize into table format"""
    members = []
    screenings = []
    responses = []
    organizations = []
    summary = {}
    
    entries = bundle.get("entry", [])
    
    # Process each resource in the bundle
    for entry in entries:
        resource = entry.get("resource", {})
        resource_type = resource.get("resourceType")
        
        if resource_type == "Patient":
            members.append(extract_member_data(resource))
        elif resource_type == "QuestionnaireResponse":
            screening_data, response_data = extract_questionnaire_response(resource)
            if screening_data:
                screenings.append(screening_data)
            responses.extend(response_data)
        elif resource_type == "Organization":
            organizations.append(extract_organization_data(resource))
    
    # Calculate summary statistics
    if screenings:
        summary = calculate_summary(screenings, responses)
    
    return {
        "members": members,
        "screenings": screenings,
        "responses": responses,
        "organizations": organizations,
        "summary": summary
    }

def extract_member_data(member: dict) -> dict:
    """Extract member information"""
    name = ""
    if member.get("name"):
        name_obj = member["name"][0] if isinstance(member["name"], list) else member["name"]
        given = " ".join(name_obj.get("given", []))
        family = name_obj.get("family", "")
        name = f"{given} {family}".strip()
    
    return {
        "member_id": member.get("id"),
        "name": name,
        "gender": member.get("gender"),
        "birth_date": member.get("birthDate"),
        "address": extract_address(member.get("address", [])),
        "phone": extract_phone(member.get("telecom", [])),
        "created_at": datetime.utcnow().isoformat()
    }

def extract_address(addresses: list) -> str:
    """Extract formatted address"""
    if not addresses:
        return ""
    
    addr = addresses[0]
    parts = []
    if addr.get("line"):
        parts.extend(addr["line"])
    if addr.get("city"):
        parts.append(addr["city"])
    if addr.get("state"):
        parts.append(addr["state"])
    if addr.get("postalCode"):
        parts.append(addr["postalCode"])
    
    return ", ".join(parts)

def extract_phone(telecoms: list) -> str:
    """Extract phone number"""
    for telecom in telecoms:
        if telecom.get("system") == "phone":
            return telecom.get("value", "")
    return ""

def extract_questionnaire_response(response: dict) -> tuple:
    """Extract questionnaire response data"""
    screening_data = {
        "session_id": response.get("id"),
        "member_id": response.get("subject", {}).get("reference", "").replace("Patient/", ""),
        "screening_date": response.get("authored") or datetime.utcnow().isoformat(),
        "status": response.get("status"),
        "questionnaire": response.get("questionnaire", ""),
        "total_safety_score": 0,
        "questions_answered": 0,
        "positive_screens": 0
    }
    
    response_data = []
    safety_score = 0
    questions_answered = 0
    positive_screens = 0
    answered_questions = set()  # Track unique questions answered
    
    # Process individual question responses
    for item in response.get("item", []):
        question_code = item.get("linkId")
        question_text = item.get("text", "")
        
        # Track that this question was answered (excluding calculated fields like safety score)
        if question_code and item.get("answer") and question_code != "95614-4":
            answered_questions.add(question_code)
        
        for answer in item.get("answer", []):
            answer_value = None
            answer_code = None
            
            if "valueCoding" in answer:
                answer_code = answer["valueCoding"].get("code")
                answer_value = answer["valueCoding"].get("display", answer_code)
            elif "valueString" in answer:
                answer_value = answer["valueString"]
            elif "valueInteger" in answer:
                answer_value = str(answer["valueInteger"])
            elif "valueBoolean" in answer:
                answer_value = "Yes" if answer["valueBoolean"] else "No"
            
            if answer_value:
                # Check for positive screens (simplified logic)
                if is_positive_screen(question_code, answer_code, answer_value):
                    positive_screens += 1
                
                # Calculate safety score for questions 9-12
                score = get_safety_score(question_code, answer_code)
                if score:
                    safety_score += score
                
                response_data.append({
                    "session_id": screening_data["session_id"],
                    "question_code": question_code,
                    "question_text": question_text,
                    "answer_code": answer_code,
                    "answer_value": answer_value,
                    "safety_score": score or 0,
                    "is_positive": is_positive_screen(question_code, answer_code, answer_value)
                })
    
    # Use the count of unique questions answered instead of individual answers
    questions_answered = len(answered_questions)
    
    screening_data.update({
        "total_safety_score": safety_score,
        "questions_answered": questions_answered,
        "positive_screens": positive_screens
    })
    
    return screening_data, response_data

def extract_organization_data(org: dict) -> dict:
    """Extract organization information"""
    return {
        "organization_id": org.get("id"),
        "name": org.get("name"),
        "type": get_organization_type(org.get("type", [])),
        "address": extract_address(org.get("address", [])),
        "phone": extract_phone(org.get("telecom", [])),
        "active": org.get("active", True)
    }

def get_organization_type(types: list) -> str:
    """Extract organization type"""
    if not types:
        return ""
    
    type_obj = types[0]
    if "coding" in type_obj:
        coding = type_obj["coding"][0]
        return coding.get("display", coding.get("code", ""))
    
    return type_obj.get("text", "")

def is_positive_screen(question_code: str, answer_code: str, answer_value: str) -> bool:
    """Determine if a response indicates a positive screen"""
    # Simplified logic - in real implementation, this would use the mapping from config
    positive_patterns = [
        "worried", "threatened", "shut off", "didn't last", "run out",
        "lack of", "help finding", "help keeping", "yes"
    ]
    
    if answer_value:
        answer_lower = answer_value.lower()
        return any(pattern in answer_lower for pattern in positive_patterns)
    
    return False

def get_safety_score(question_code: str, answer_code: str) -> int:
    """Calculate safety score for questions 9-12"""
    # Safety questions mapping (simplified)
    safety_mappings = {
        "LA6270-8": 1,    # Never
        "LA10066-1": 2,   # Rarely
        "LA10082-8": 3,   # Sometimes
        "LA16644-9": 4,   # Fairly often
        "LA6482-9": 5     # Frequently
    }
    
    # Check if this is a safety question (9-12) by question code
    safety_questions = ["95618-5", "95617-7", "95616-9", "95615-1"]
    
    if question_code in safety_questions and answer_code in safety_mappings:
        return safety_mappings[answer_code]
    
    return 0

def calculate_summary(screenings: list, responses: list) -> dict:
    """Calculate summary statistics"""
    if not screenings:
        return {}
    
    screening = screenings[0]  # Assuming one screening session per bundle
    
    return {
        "total_safety_score": screening.get("total_safety_score", 0),
        "high_risk": screening.get("total_safety_score", 0) >= 11,
        "positive_screens": screening.get("positive_screens", 0),
        "questions_answered": screening.get("questions_answered", 0),
        "completion_rate": round((screening.get("questions_answered", 0) / 12) * 100, 1)
    }

# Initialize FHIR processor
fhir_processor = FHIRBundleProcessor()

@app.post("/api/process-bundle")
async def process_bundle(bundle: dict, db: Session = Depends(get_db)):
    """Process a FHIR bundle and extract data into table format (for web interface)"""
    try:
        logging.info(f"Processing FHIR bundle: {bundle.get('id', 'unknown')}")
        
        # Validate bundle structure
        if not isinstance(bundle, dict) or bundle.get("resourceType") != "Bundle":
            raise HTTPException(status_code=400, detail="Invalid FHIR Bundle structure")
        
        # Extract bundle information
        bundle_info = {
            "id": bundle.get("id"),
            "type": bundle.get("type"),
            "total": len(bundle.get("entry", []))
        }
        
        # Process bundle entries using original logic
        result = extract_bundle_data(bundle)
        result["bundle_info"] = bundle_info
        
        # If database is available, also save to database
        if db:
            try:
                db_result = fhir_processor.process_bundle(bundle, db)
                result["database_saved"] = True
                result["db_result"] = db_result
            except Exception as e:
                logging.warning(f"Database save failed: {e}")
                result["database_saved"] = False
                result["db_error"] = str(e)
        else:
            result["database_saved"] = False
        
        logging.info(f"Successfully processed bundle {bundle_info['id']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error processing bundle: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/fhir/Bundle")
async def receive_fhir_bundle(bundle: dict, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Receive and process FHIR Bundle containing HRSN screening data (authenticated endpoint)"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Generate processing ID
        processing_id = str(uuid.uuid4())
        
        # Basic validation
        if not isinstance(bundle, dict) or bundle.get("resourceType") != "Bundle":
            raise HTTPException(status_code=400, detail="Invalid FHIR Bundle structure")
        
        bundle_id = bundle.get("id")
        if not bundle_id:
            raise HTTPException(status_code=400, detail="Bundle must have an ID")
        
        logging.info(f"Received FHIR Bundle {bundle_id} for processing {processing_id}")
        
        # Process bundle
        result = fhir_processor.process_bundle(bundle, db)
        
        return {
            "bundle_id": bundle_id,
            "processing_id": processing_id,
            "status": "completed",
            "message": "Bundle processed successfully",
            "received_at": datetime.utcnow().isoformat(),
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error receiving bundle: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    print(f"Starting server on port {port}")
    uvicorn.run("simple_main:app", host="0.0.0.0", port=port, log_level="info")