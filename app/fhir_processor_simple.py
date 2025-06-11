# app/fhir_processor_simple.py
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import logging

from .models import Member, Organization, ScreeningSession, ScreeningResponse
from .config import HRSN_QUESTION_MAPPINGS

logger = logging.getLogger(__name__)

class FHIRBundleProcessor:
    """Simple FHIR bundle processor for basic functionality"""
    
    def __init__(self):
        self.safety_questions = ["95618-5", "95617-7", "95616-9", "95615-1"]
    
    async def process_bundle(self, bundle_dict: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Main entry point for processing FHIR bundles
        """
        try:
            logger.info(f"Processing FHIR bundle: {bundle_dict.get('id', 'unknown')}")
            
            # Basic validation
            if not isinstance(bundle_dict, dict) or bundle_dict.get("resourceType") != "Bundle":
                raise ValueError("Invalid FHIR Bundle structure")
            
            bundle_id = bundle_dict.get("id")
            entries = bundle_dict.get("entry", [])
            
            result = {
                "bundle_id": bundle_id,
                "members_processed": 0,
                "screenings_processed": 0,
                "organizations_processed": 0,
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
                elif resource_type == "Organization":
                    self._process_organization(resource, db)
                    result["organizations_processed"] += 1
            
            db.commit()
            logger.info(f"Successfully processed bundle {bundle_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing bundle: {e}")
            db.rollback()
            raise
    
    def _process_member(self, patient_resource: Dict[str, Any], db: Session) -> Member:
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
        if addresses and len(addresses) > 0:
            addr = addresses[0]
            lines = addr.get("line", [])
            if lines:
                address_line1 = lines[0] if isinstance(lines, list) else str(lines)
            city = addr.get("city", "")
            state = addr.get("state", "")
            zip_code = addr.get("postalCode", "")
        
        # Create new member
        member = Member(
            fhir_id=fhir_id,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=birth_date,
            gender=gender,
            address_line1=address_line1,
            city=city,
            state=state,
            zip_code=zip_code
        )
        
        db.add(member)
        db.flush()  # Get the ID
        return member
    
    def _process_questionnaire_response(self, qr_resource: Dict[str, Any], db: Session):
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
                logger.warning(f"Member not found for reference: {subject_ref}")
                return
        else:
            logger.warning(f"Invalid subject reference: {subject_ref}")
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
        
    def _process_organization(self, org_resource: Dict[str, Any], db: Session) -> Organization:
        """Process a FHIR Organization resource"""
        
        fhir_id = org_resource.get("id")
        if not fhir_id:
            raise ValueError("Organization resource missing ID")
        
        # Check for existing organization
        existing_org = db.query(Organization).filter(Organization.fhir_id == fhir_id).first()
        if existing_org:
            return existing_org
        
        name = org_resource.get("name", "")
        
        # Extract organization type
        org_types = org_resource.get("type", [])
        org_type = ""
        if org_types and len(org_types) > 0:
            type_coding = org_types[0].get("coding", [])
            if type_coding and len(type_coding) > 0:
                org_type = type_coding[0].get("code", "")
        
        # Extract address
        addresses = org_resource.get("address", [])
        address_line1 = ""
        city = ""
        state = ""
        zip_code = ""
        if addresses and len(addresses) > 0:
            addr = addresses[0]
            lines = addr.get("line", [])
            if lines:
                address_line1 = lines[0] if isinstance(lines, list) else str(lines)
            city = addr.get("city", "")
            state = addr.get("state", "")
            zip_code = addr.get("postalCode", "")
        
        organization = Organization(
            fhir_id=fhir_id,
            name=name,
            organization_type=org_type,
            address_line1=address_line1,
            city=city,
            state=state,
            zip_code=zip_code
        )
        
        db.add(organization)
        db.flush()
        return organization