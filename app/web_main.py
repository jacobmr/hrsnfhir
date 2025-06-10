from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from datetime import datetime
from typing import Dict, Any, List
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="HRSN FHIR Bundle Processor",
    description="Web interface for processing HRSN FHIR data bundles",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    with open("app/static/index.html", "r") as f:
        return f.read()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "HRSN FHIR Processor Web Interface",
        "version": "1.0.0"
    }

@app.post("/api/process-bundle")
async def process_bundle(bundle: Dict[str, Any]):
    """
    Process a FHIR bundle and extract data into table format
    """
    try:
        logger.info(f"Processing FHIR bundle: {bundle.get('id', 'unknown')}")
        
        # Validate bundle structure
        if not isinstance(bundle, dict) or bundle.get("resourceType") != "Bundle":
            raise HTTPException(status_code=400, detail="Invalid FHIR Bundle structure")
        
        # Extract bundle information
        bundle_info = {
            "id": bundle.get("id"),
            "type": bundle.get("type"),
            "total": len(bundle.get("entry", []))
        }
        
        # Process bundle entries
        result = extract_bundle_data(bundle)
        result["bundle_info"] = bundle_info
        
        logger.info(f"Successfully processed bundle {bundle_info['id']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing bundle: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

def extract_bundle_data(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract data from FHIR bundle and organize into table format
    """
    patients = []
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
            patients.append(extract_patient_data(resource))
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
        "patients": patients,
        "screenings": screenings,
        "responses": responses,
        "organizations": organizations,
        "summary": summary
    }

def extract_patient_data(patient: Dict[str, Any]) -> Dict[str, Any]:
    """Extract patient information"""
    name = ""
    if patient.get("name"):
        name_obj = patient["name"][0] if isinstance(patient["name"], list) else patient["name"]
        given = " ".join(name_obj.get("given", []))
        family = name_obj.get("family", "")
        name = f"{given} {family}".strip()
    
    return {
        "patient_id": patient.get("id"),
        "name": name,
        "gender": patient.get("gender"),
        "birth_date": patient.get("birthDate"),
        "address": extract_address(patient.get("address", [])),
        "phone": extract_phone(patient.get("telecom", [])),
        "created_at": datetime.utcnow().isoformat()
    }

def extract_address(addresses: List[Dict]) -> str:
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

def extract_phone(telecoms: List[Dict]) -> str:
    """Extract phone number"""
    for telecom in telecoms:
        if telecom.get("system") == "phone":
            return telecom.get("value", "")
    return ""

def extract_questionnaire_response(response: Dict[str, Any]) -> tuple:
    """Extract questionnaire response data"""
    screening_data = {
        "session_id": response.get("id"),
        "patient_id": response.get("subject", {}).get("reference", "").replace("Patient/", ""),
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
    
    # Process individual question responses
    for item in response.get("item", []):
        question_code = item.get("linkId")
        question_text = item.get("text", "")
        
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
                questions_answered += 1
                
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
    
    screening_data.update({
        "total_safety_score": safety_score,
        "questions_answered": questions_answered,
        "positive_screens": positive_screens
    })
    
    return screening_data, response_data

def extract_organization_data(org: Dict[str, Any]) -> Dict[str, Any]:
    """Extract organization information"""
    return {
        "organization_id": org.get("id"),
        "name": org.get("name"),
        "type": get_organization_type(org.get("type", [])),
        "address": extract_address(org.get("address", [])),
        "phone": extract_phone(org.get("telecom", [])),
        "active": org.get("active", True)
    }

def get_organization_type(types: List[Dict]) -> str:
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

def calculate_summary(screenings: List[Dict], responses: List[Dict]) -> Dict[str, Any]:
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "web_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )