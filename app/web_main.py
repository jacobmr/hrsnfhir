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

# Simple in-memory database for member data
member_database = {
    "members": [],
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
        store_member_data(result)
        
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

def extract_member_data(member: Dict[str, Any]) -> Dict[str, Any]:
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

def store_member_data(result: Dict[str, Any]):
    """Store extracted member data in our simple database"""
    global member_database
    
    # Add members (avoid duplicates by member ID)
    for member in result.get("members", []):
        member_id = member.get("member_id")
        if member_id and not any(m.get("member_id") == member_id for m in member_database["members"]):
            member_database["members"].append(member)
    
    # Add screenings
    member_database["screenings"].extend(result.get("screenings", []))
    
    # Add responses
    member_database["responses"].extend(result.get("responses", []))

@app.post("/api/chatbot")
async def chatbot_query(query_data: Dict[str, Any]):
    """
    Chatbot endpoint to answer questions about member data
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
    total_members = len(member_database["members"])
    
    if total_members == 0:
        return {
            "answer": "No member data available. Please upload some FHIR bundles first to populate the database.",
            "data": [],
            "summary": {"total_members": 0}
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
    
    # High risk members
    elif "high risk" in question or "risk" in question:
        return analyze_high_risk_members()
    
    # Member list/count questions
    elif "how many" in question or "count" in question or "number" in question:
        return analyze_member_counts(question)
    
    # Member details questions
    elif "who" in question or "which members" in question or "tell me" in question:
        return analyze_member_details(question)
    
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
                     f"• Food insecurity: 'How many members have food insecurity?'\n" +
                     f"• Housing issues: 'Which members have housing problems?'\n" +
                     f"• Transportation: 'Tell me about transportation issues'\n" +
                     f"• Safety concerns: 'How many members have safety concerns?'\n" +
                     f"• High risk members: 'Who are the high risk members?'\n" +
                     f"• General statistics: 'Show me member statistics'\n\n" +
                     f"Current database: {total_members} members",
            "data": [],
            "summary": {"total_members": total_members}
        }

def analyze_food_insecurity() -> Dict[str, Any]:
    """Analyze food insecurity among members"""
    total_members = len(member_database["members"])
    food_insecure_members = []
    
    # Check responses for food insecurity indicators
    for response in member_database["responses"]:
        question_code = response.get("question_code", "")
        answer_value = response.get("answer_value", "").lower()
        member_id = response.get("session_id", "")
        
        # Food insecurity questions: 88122-7 and 88123-5
        if question_code in ["88122-7", "88123-5"]:
            if "often true" in answer_value or "sometimes true" in answer_value:
                # Find member details
                member = next((m for m in member_database["members"] 
                              if m.get("member_id") == member_id), None)
                if member and member not in food_insecure_members:
                    food_insecure_members.append(member)
    
    count = len(food_insecure_members)
    percentage = round((count / total_members) * 100, 1) if total_members > 0 else 0
    
    # Create member links
    member_data = []
    for member in food_insecure_members:
        member_data.append({
            "name": member.get("name", "Unknown"),
            "member_id": member.get("member_id", ""),
            "link": f"/member/{member.get('member_id', '')}"
        })
    
    return {
        "answer": f"Food Insecurity Analysis:\n{count} out of {total_members} members ({percentage}%) have food insecurity issues.",
        "data": member_data,
        "summary": {
            "total_members": total_members,
            "affected_count": count,
            "percentage": percentage,
            "condition": "food_insecurity"
        }
    }

def analyze_housing_issues() -> Dict[str, Any]:
    """Analyze housing issues among members"""
    total_members = len(member_database["members"])
    housing_issues_members = []
    
    for response in member_database["responses"]:
        question_code = response.get("question_code", "")
        answer_value = response.get("answer_value", "").lower()
        member_id = response.get("session_id", "")
        
        # Housing questions: 71802-3 (living situation) and 96778-6 (housing problems)
        if question_code in ["71802-3", "96778-6"]:
            if ("not have a steady place" in answer_value or 
                "worried about losing" in answer_value or
                "pests" in answer_value or
                "mold" in answer_value or
                "lack of heat" in answer_value):
                
                member = next((m for m in member_database["members"] 
                              if m.get("member_id") == member_id), None)
                if member and member not in housing_issues_members:
                    housing_issues_members.append(member)
    
    count = len(housing_issues_members)
    percentage = round((count / total_members) * 100, 1) if total_members > 0 else 0
    
    member_data = []
    for member in housing_issues_members:
        member_data.append({
            "name": member.get("name", "Unknown"),
            "member_id": member.get("member_id", ""),
            "link": f"/member/{member.get('member_id', '')}"
        })
    
    return {
        "answer": f"Housing Issues Analysis:\n{count} out of {total_members} members ({percentage}%) have housing-related concerns.",
        "data": member_data,
        "summary": {
            "total_members": total_members,
            "affected_count": count,
            "percentage": percentage,
            "condition": "housing_issues"
        }
    }

def analyze_transportation_issues() -> Dict[str, Any]:
    """Analyze transportation issues among members"""
    total_members = len(member_database["members"])
    transport_issues_members = []
    
    for response in member_database["responses"]:
        question_code = response.get("question_code", "")
        answer_value = response.get("answer_value", "").lower()
        member_id = response.get("session_id", "")
        
        # Transportation question: 93030-5
        if question_code == "93030-5" and "yes" in answer_value:
            member = next((m for m in member_database["members"] 
                          if m.get("member_id") == member_id), None)
            if member and member not in transport_issues_members:
                transport_issues_members.append(member)
    
    count = len(transport_issues_members)
    percentage = round((count / total_members) * 100, 1) if total_members > 0 else 0
    
    member_data = []
    for member in transport_issues_members:
        member_data.append({
            "name": member.get("name", "Unknown"),
            "member_id": member.get("member_id", ""),
            "link": f"/member/{member.get('member_id', '')}"
        })
    
    return {
        "answer": f"Transportation Issues Analysis:\n{count} out of {total_members} members ({percentage}%) have transportation barriers.",
        "data": member_data,
        "summary": {
            "total_members": total_members,
            "affected_count": count,
            "percentage": percentage,
            "condition": "transportation_issues"
        }
    }

def analyze_safety_concerns() -> Dict[str, Any]:
    """Analyze safety/violence concerns among members"""
    total_members = len(member_database["members"])
    high_risk_members = []
    
    # Group safety scores by member
    member_safety_scores = {}
    for screening in member_database["screenings"]:
        member_id = screening.get("member_id", "")
        safety_score = screening.get("total_safety_score", 0)
        if member_id:
            member_safety_scores[member_id] = safety_score
    
    # Find high-risk members (safety score >= 11)
    for member_id, safety_score in member_safety_scores.items():
        if safety_score >= 11:
            member = next((m for m in member_database["members"] 
                          if m.get("member_id") == member_id), None)
            if member:
                high_risk_members.append({
                    **member,
                    "safety_score": safety_score
                })
    
    count = len(high_risk_members)
    percentage = round((count / total_members) * 100, 1) if total_members > 0 else 0
    
    member_data = []
    for member in high_risk_members:
        member_data.append({
            "name": member.get("name", "Unknown"),
            "member_id": member.get("member_id", ""),
            "safety_score": member.get("safety_score", 0),
            "link": f"/member/{member.get('member_id', '')}"
        })
    
    return {
        "answer": f"Safety Concerns Analysis:\n{count} out of {total_members} members ({percentage}%) have high safety risk (score ≥11).",
        "data": member_data,
        "summary": {
            "total_members": total_members,
            "high_risk_count": count,
            "percentage": percentage,
            "condition": "safety_concerns"
        }
    }

def analyze_high_risk_members() -> Dict[str, Any]:
    """Analyze high-risk members based on safety scores"""
    return analyze_safety_concerns()  # Same logic

def get_general_statistics() -> Dict[str, Any]:
    """Get general statistics about all members"""
    total_members = len(member_database["members"])
    total_screenings = len(member_database["screenings"])
    
    # Calculate various statistics
    high_risk_count = 0
    food_insecure_count = 0
    housing_issues_count = 0
    
    for screening in member_database["screenings"]:
        if screening.get("total_safety_score", 0) >= 11:
            high_risk_count += 1
    
    # Quick counts for other conditions
    food_result = analyze_food_insecurity()
    housing_result = analyze_housing_issues()
    
    return {
        "answer": f"Member Database Statistics:\n" +
                 f"• Total Members: {total_members}\n" +
                 f"• Total Screenings: {total_screenings}\n" +
                 f"• High Safety Risk: {high_risk_count} ({round((high_risk_count/total_members)*100,1) if total_members>0 else 0}%)\n" +
                 f"• Food Insecurity: {food_result['summary']['affected_count']} ({food_result['summary']['percentage']}%)\n" +
                 f"• Housing Issues: {housing_result['summary']['affected_count']} ({housing_result['summary']['percentage']}%)",
        "data": [],
        "summary": {
            "total_members": total_members,
            "total_screenings": total_screenings,
            "high_risk_count": high_risk_count,
            "food_insecurity": food_result['summary']['affected_count'],
            "housing_issues": housing_result['summary']['affected_count']
        }
    }

def analyze_member_counts(question: str) -> Dict[str, Any]:
    """Handle 'how many' type questions"""
    if "food" in question:
        return analyze_food_insecurity()
    elif "housing" in question or "homeless" in question:
        return analyze_housing_issues()
    elif "safety" in question or "risk" in question:
        return analyze_safety_concerns()
    else:
        return get_general_statistics()

def analyze_member_details(question: str) -> Dict[str, Any]:
    """Handle 'who' or 'which members' type questions"""
    if "food" in question:
        return analyze_food_insecurity()
    elif "housing" in question or "homeless" in question:
        return analyze_housing_issues()
    elif "safety" in question or "risk" in question:
        return analyze_safety_concerns()
    else:
        # Return all members
        total_members = len(member_database["members"])
        member_data = []
        for member in member_database["members"]:
            member_data.append({
                "name": member.get("name", "Unknown"),
                "member_id": member.get("member_id", ""),
                "gender": member.get("gender", ""),
                "birth_date": member.get("birth_date", ""),
                "link": f"/member/{member.get('member_id', '')}"
            })
        
        return {
            "answer": f"All Members in Database ({total_members} total):",
            "data": member_data,
            "summary": {"total_members": total_members}
        }

def get_database_overview() -> Dict[str, Any]:
    """Get comprehensive database overview with all member details"""
    total_members = len(member_database["members"])
    total_screenings = len(member_database["screenings"])
    total_responses = len(member_database["responses"])
    
    if total_members == 0:
        return {
            "answer": "Database is empty. Upload some FHIR bundles to populate member data.",
            "data": [],
            "summary": {"total_members": 0}
        }
    
    # Collect all member data with their screening info
    member_overview = []
    
    for member in member_database["members"]:
        member_id = member.get("member_id", "")
        
        # Find screening data for this member
        screening = next((s for s in member_database["screenings"] 
                         if s.get("member_id") == member_id), {})
        
        # Count responses for this member
        member_responses = [r for r in member_database["responses"] 
                           if r.get("session_id") == member_id]
        
        member_overview.append({
            "name": member.get("name", "Unknown"),
            "member_id": member_id,
            "gender": member.get("gender", "N/A"),
            "birth_date": member.get("birth_date", "N/A"),
            "address": member.get("address", "N/A"),
            "safety_score": screening.get("total_safety_score", 0),
            "high_risk": screening.get("total_safety_score", 0) >= 11,
            "questions_answered": screening.get("questions_answered", 0),
            "positive_screens": screening.get("positive_screens", 0),
            "response_count": len(member_responses),
            "link": f"/member/{member_id}"
        })
    
    # Sort by safety score (highest risk first)
    member_overview.sort(key=lambda x: x.get("safety_score", 0), reverse=True)
    
    answer = f"Database Overview - Complete Member Details:\n"
    answer += f"📊 Total: {total_members} members, {total_screenings} screenings, {total_responses} responses\n\n"
    
    for i, member in enumerate(member_overview, 1):
        risk_indicator = "⚠️ HIGH RISK" if member["high_risk"] else "✅ Low Risk"
        answer += f"{i}. {member['name']} ({member['gender']}, {member['birth_date']})\n"
        answer += f"   Safety Score: {member['safety_score']} - {risk_indicator}\n"
        answer += f"   Questions Answered: {member['questions_answered']}/12\n"
        answer += f"   Positive Screens: {member['positive_screens']}\n"
        answer += f"   Address: {member['address']}\n\n"
    
    return {
        "answer": answer.strip(),
        "data": member_overview,
        "summary": {
            "total_members": total_members,
            "total_screenings": total_screenings,
            "total_responses": total_responses,
            "high_risk_count": sum(1 for m in member_overview if m["high_risk"])
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