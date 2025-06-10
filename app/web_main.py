from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from datetime import datetime
from typing import Dict, Any, List
import json
import logging
import re
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="HRSN FHIR Bundle Processor",
    description="Web interface for processing HRSN FHIR data bundles",
    version="1.0.0"
)

# Simple in-memory database for patient data
patient_database = {
    "patients": [],
    "screenings": [],
    "responses": []
}

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
        
        # Store data in our simple database for chatbot queries
        store_patient_data(result)
        
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

def store_patient_data(result: Dict[str, Any]):
    """Store extracted patient data in our simple database"""
    global patient_database
    
    # Add patients (avoid duplicates by patient ID)
    for patient in result.get("patients", []):
        patient_id = patient.get("patient_id")
        if patient_id and not any(p.get("patient_id") == patient_id for p in patient_database["patients"]):
            patient_database["patients"].append(patient)
    
    # Add screenings
    patient_database["screenings"].extend(result.get("screenings", []))
    
    # Add responses
    patient_database["responses"].extend(result.get("responses", []))

@app.post("/api/chatbot")
async def chatbot_query(query_data: Dict[str, Any]):
    """
    Chatbot endpoint to answer questions about patient data
    """
    try:
        question = query_data.get("question", "").strip().lower()
        
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        logger.info(f"Chatbot query: {question}")
        
        # Process the question and generate response
        response = process_chatbot_query(question)
        
        return {
            "question": query_data.get("question"),
            "answer": response["answer"],
            "data": response.get("data", []),
            "summary": response.get("summary", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")

def process_chatbot_query(question: str) -> Dict[str, Any]:
    """Process chatbot questions and return structured responses"""
    
    # Get current database stats
    total_patients = len(patient_database["patients"])
    
    if total_patients == 0:
        return {
            "answer": "No patient data available. Please upload some FHIR bundles first to populate the database.",
            "data": [],
            "summary": {"total_patients": 0}
        }
    
    # Food insecurity questions
    if "food" in question and ("insecurity" in question or "insecure" in question):
        return analyze_food_insecurity()
    
    # Housing questions
    elif "housing" in question or "homeless" in question or "shelter" in question:
        return analyze_housing_issues()
    
    # Transportation questions
    elif "transport" in question or "transportation" in question:
        return analyze_transportation_issues()
    
    # Safety/violence questions
    elif "safety" in question or "violence" in question or "hurt" in question:
        return analyze_safety_concerns()
    
    # High risk patients
    elif "high risk" in question or "risk" in question:
        return analyze_high_risk_patients()
    
    # Patient list/count questions
    elif "how many" in question or "count" in question or "number" in question:
        return analyze_patient_counts(question)
    
    # Patient details questions
    elif "who" in question or "which patients" in question or "tell me" in question:
        return analyze_patient_details(question)
    
    # General statistics
    elif "stats" in question or "statistics" in question or "summary" in question:
        return get_general_statistics()
    
    # Database overview
    elif "database" in question or "overview" in question or "show all" in question:
        return get_database_overview()
    
    # Default response
    else:
        return {
            "answer": f"I can answer questions about:\n" +
                     f"• Food insecurity: 'How many patients have food insecurity?'\n" +
                     f"• Housing issues: 'Which patients have housing problems?'\n" +
                     f"• Transportation: 'Tell me about transportation issues'\n" +
                     f"• Safety concerns: 'How many patients have safety concerns?'\n" +
                     f"• High risk patients: 'Who are the high risk patients?'\n" +
                     f"• General statistics: 'Show me patient statistics'\n\n" +
                     f"Current database: {total_patients} patients",
            "data": [],
            "summary": {"total_patients": total_patients}
        }

def analyze_food_insecurity() -> Dict[str, Any]:
    """Analyze food insecurity among patients"""
    total_patients = len(patient_database["patients"])
    food_insecure_patients = []
    
    # Check responses for food insecurity indicators
    for response in patient_database["responses"]:
        question_code = response.get("question_code", "")
        answer_value = response.get("answer_value", "").lower()
        patient_id = response.get("session_id", "")
        
        # Food insecurity questions: 88122-7 and 88123-5
        if question_code in ["88122-7", "88123-5"]:
            if "often true" in answer_value or "sometimes true" in answer_value:
                # Find patient details
                patient = next((p for p in patient_database["patients"] 
                              if p.get("patient_id") == patient_id), None)
                if patient and patient not in food_insecure_patients:
                    food_insecure_patients.append(patient)
    
    count = len(food_insecure_patients)
    percentage = round((count / total_patients) * 100, 1) if total_patients > 0 else 0
    
    # Create patient links
    patient_data = []
    for patient in food_insecure_patients:
        patient_data.append({
            "name": patient.get("name", "Unknown"),
            "patient_id": patient.get("patient_id", ""),
            "link": f"/patient/{patient.get('patient_id', '')}"
        })
    
    return {
        "answer": f"Food Insecurity Analysis:\n{count} out of {total_patients} patients ({percentage}%) have food insecurity issues.",
        "data": patient_data,
        "summary": {
            "total_patients": total_patients,
            "affected_count": count,
            "percentage": percentage,
            "condition": "food_insecurity"
        }
    }

def analyze_housing_issues() -> Dict[str, Any]:
    """Analyze housing issues among patients"""
    total_patients = len(patient_database["patients"])
    housing_issues_patients = []
    
    for response in patient_database["responses"]:
        question_code = response.get("question_code", "")
        answer_value = response.get("answer_value", "").lower()
        patient_id = response.get("session_id", "")
        
        # Housing questions: 71802-3 (living situation) and 96778-6 (housing problems)
        if question_code in ["71802-3", "96778-6"]:
            if ("not have a steady place" in answer_value or 
                "worried about losing" in answer_value or
                "pests" in answer_value or
                "mold" in answer_value or
                "lack of heat" in answer_value):
                
                patient = next((p for p in patient_database["patients"] 
                              if p.get("patient_id") == patient_id), None)
                if patient and patient not in housing_issues_patients:
                    housing_issues_patients.append(patient)
    
    count = len(housing_issues_patients)
    percentage = round((count / total_patients) * 100, 1) if total_patients > 0 else 0
    
    patient_data = []
    for patient in housing_issues_patients:
        patient_data.append({
            "name": patient.get("name", "Unknown"),
            "patient_id": patient.get("patient_id", ""),
            "link": f"/patient/{patient.get('patient_id', '')}"
        })
    
    return {
        "answer": f"Housing Issues Analysis:\n{count} out of {total_patients} patients ({percentage}%) have housing-related concerns.",
        "data": patient_data,
        "summary": {
            "total_patients": total_patients,
            "affected_count": count,
            "percentage": percentage,
            "condition": "housing_issues"
        }
    }

def analyze_transportation_issues() -> Dict[str, Any]:
    """Analyze transportation issues among patients"""
    total_patients = len(patient_database["patients"])
    transport_issues_patients = []
    
    for response in patient_database["responses"]:
        question_code = response.get("question_code", "")
        answer_value = response.get("answer_value", "").lower()
        patient_id = response.get("session_id", "")
        
        # Transportation question: 93030-5
        if question_code == "93030-5" and "yes" in answer_value:
            patient = next((p for p in patient_database["patients"] 
                          if p.get("patient_id") == patient_id), None)
            if patient and patient not in transport_issues_patients:
                transport_issues_patients.append(patient)
    
    count = len(transport_issues_patients)
    percentage = round((count / total_patients) * 100, 1) if total_patients > 0 else 0
    
    patient_data = []
    for patient in transport_issues_patients:
        patient_data.append({
            "name": patient.get("name", "Unknown"),
            "patient_id": patient.get("patient_id", ""),
            "link": f"/patient/{patient.get('patient_id', '')}"
        })
    
    return {
        "answer": f"Transportation Issues Analysis:\n{count} out of {total_patients} patients ({percentage}%) have transportation barriers.",
        "data": patient_data,
        "summary": {
            "total_patients": total_patients,
            "affected_count": count,
            "percentage": percentage,
            "condition": "transportation_issues"
        }
    }

def analyze_safety_concerns() -> Dict[str, Any]:
    """Analyze safety/violence concerns among patients"""
    total_patients = len(patient_database["patients"])
    high_risk_patients = []
    
    # Group safety scores by patient
    patient_safety_scores = {}
    for screening in patient_database["screenings"]:
        patient_id = screening.get("patient_id", "")
        safety_score = screening.get("total_safety_score", 0)
        if patient_id:
            patient_safety_scores[patient_id] = safety_score
    
    # Find high-risk patients (safety score >= 11)
    for patient_id, safety_score in patient_safety_scores.items():
        if safety_score >= 11:
            patient = next((p for p in patient_database["patients"] 
                          if p.get("patient_id") == patient_id), None)
            if patient:
                high_risk_patients.append({
                    **patient,
                    "safety_score": safety_score
                })
    
    count = len(high_risk_patients)
    percentage = round((count / total_patients) * 100, 1) if total_patients > 0 else 0
    
    patient_data = []
    for patient in high_risk_patients:
        patient_data.append({
            "name": patient.get("name", "Unknown"),
            "patient_id": patient.get("patient_id", ""),
            "safety_score": patient.get("safety_score", 0),
            "link": f"/patient/{patient.get('patient_id', '')}"
        })
    
    return {
        "answer": f"Safety Concerns Analysis:\n{count} out of {total_patients} patients ({percentage}%) have high safety risk (score ≥11).",
        "data": patient_data,
        "summary": {
            "total_patients": total_patients,
            "high_risk_count": count,
            "percentage": percentage,
            "condition": "safety_concerns"
        }
    }

def analyze_high_risk_patients() -> Dict[str, Any]:
    """Analyze high-risk patients based on safety scores"""
    return analyze_safety_concerns()  # Same logic

def get_general_statistics() -> Dict[str, Any]:
    """Get general statistics about all patients"""
    total_patients = len(patient_database["patients"])
    total_screenings = len(patient_database["screenings"])
    
    # Calculate various statistics
    high_risk_count = 0
    food_insecure_count = 0
    housing_issues_count = 0
    
    for screening in patient_database["screenings"]:
        if screening.get("total_safety_score", 0) >= 11:
            high_risk_count += 1
    
    # Quick counts for other conditions
    food_result = analyze_food_insecurity()
    housing_result = analyze_housing_issues()
    
    return {
        "answer": f"Patient Database Statistics:\n" +
                 f"• Total Patients: {total_patients}\n" +
                 f"• Total Screenings: {total_screenings}\n" +
                 f"• High Safety Risk: {high_risk_count} ({round((high_risk_count/total_patients)*100,1) if total_patients>0 else 0}%)\n" +
                 f"• Food Insecurity: {food_result['summary']['affected_count']} ({food_result['summary']['percentage']}%)\n" +
                 f"• Housing Issues: {housing_result['summary']['affected_count']} ({housing_result['summary']['percentage']}%)",
        "data": [],
        "summary": {
            "total_patients": total_patients,
            "total_screenings": total_screenings,
            "high_risk_count": high_risk_count,
            "food_insecurity": food_result['summary']['affected_count'],
            "housing_issues": housing_result['summary']['affected_count']
        }
    }

def analyze_patient_counts(question: str) -> Dict[str, Any]:
    """Handle 'how many' type questions"""
    if "food" in question:
        return analyze_food_insecurity()
    elif "housing" in question or "homeless" in question:
        return analyze_housing_issues()
    elif "safety" in question or "risk" in question:
        return analyze_safety_concerns()
    else:
        return get_general_statistics()

def analyze_patient_details(question: str) -> Dict[str, Any]:
    """Handle 'who' or 'which patients' type questions"""
    if "food" in question:
        return analyze_food_insecurity()
    elif "housing" in question or "homeless" in question:
        return analyze_housing_issues()
    elif "safety" in question or "risk" in question:
        return analyze_safety_concerns()
    else:
        # Return all patients
        total_patients = len(patient_database["patients"])
        patient_data = []
        for patient in patient_database["patients"]:
            patient_data.append({
                "name": patient.get("name", "Unknown"),
                "patient_id": patient.get("patient_id", ""),
                "gender": patient.get("gender", ""),
                "birth_date": patient.get("birth_date", ""),
                "link": f"/patient/{patient.get('patient_id', '')}"
            })
        
        return {
            "answer": f"All Patients in Database ({total_patients} total):",
            "data": patient_data,
            "summary": {"total_patients": total_patients}
        }

def get_database_overview() -> Dict[str, Any]:
    """Get comprehensive database overview with all patient details"""
    total_patients = len(patient_database["patients"])
    total_screenings = len(patient_database["screenings"])
    total_responses = len(patient_database["responses"])
    
    if total_patients == 0:
        return {
            "answer": "Database is empty. Upload some FHIR bundles to populate patient data.",
            "data": [],
            "summary": {"total_patients": 0}
        }
    
    # Collect all patient data with their screening info
    patient_overview = []
    
    for patient in patient_database["patients"]:
        patient_id = patient.get("patient_id", "")
        
        # Find screening data for this patient
        screening = next((s for s in patient_database["screenings"] 
                         if s.get("patient_id") == patient_id), {})
        
        # Count responses for this patient
        patient_responses = [r for r in patient_database["responses"] 
                           if r.get("session_id") == patient_id]
        
        patient_overview.append({
            "name": patient.get("name", "Unknown"),
            "patient_id": patient_id,
            "gender": patient.get("gender", "N/A"),
            "birth_date": patient.get("birth_date", "N/A"),
            "address": patient.get("address", "N/A"),
            "safety_score": screening.get("total_safety_score", 0),
            "high_risk": screening.get("total_safety_score", 0) >= 11,
            "questions_answered": screening.get("questions_answered", 0),
            "positive_screens": screening.get("positive_screens", 0),
            "response_count": len(patient_responses),
            "link": f"/patient/{patient_id}"
        })
    
    # Sort by safety score (highest risk first)
    patient_overview.sort(key=lambda x: x.get("safety_score", 0), reverse=True)
    
    answer = f"Database Overview - Complete Patient Details:\n"
    answer += f"📊 Total: {total_patients} patients, {total_screenings} screenings, {total_responses} responses\n\n"
    
    for i, patient in enumerate(patient_overview, 1):
        risk_indicator = "⚠️ HIGH RISK" if patient["high_risk"] else "✅ Low Risk"
        answer += f"{i}. {patient['name']} ({patient['gender']}, {patient['birth_date']})\n"
        answer += f"   Safety Score: {patient['safety_score']} - {risk_indicator}\n"
        answer += f"   Questions Answered: {patient['questions_answered']}/12\n"
        answer += f"   Positive Screens: {patient['positive_screens']}\n"
        answer += f"   Address: {patient['address']}\n\n"
    
    return {
        "answer": answer.strip(),
        "data": patient_overview,
        "summary": {
            "total_patients": total_patients,
            "total_screenings": total_screenings,
            "total_responses": total_responses,
            "high_risk_count": sum(1 for p in patient_overview if p["high_risk"])
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "web_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )