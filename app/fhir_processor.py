# app/fhir_processor.py
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from fhir.resources.bundle import Bundle
from fhir.resources.patient import Patient as FHIRPatient
from fhir.resources.observation import Observation as FHIRObservation
from fhir.resources.encounter import Encounter as FHIREncounter
from fhir.resources.organization import Organization as FHIROrganization
from fhir.resources.consent import Consent as FHIRConsent
from datetime import datetime
import logging

from .models import (
    Member, Organization, Encounter, ScreeningSession, 
    ScreeningResponse, BundleProcessingLog
)
from .config import HRSN_QUESTION_MAPPINGS, ORGANIZATION_TYPE_MAPPINGS, ENCOUNTER_TYPE_MAPPINGS

logger = logging.getLogger(__name__)

class FHIRBundleProcessor:
    """Processes HRSN FHIR bundles and extracts data into SQL database"""
    
    def __init__(self):
        self.safety_questions = ["95618-5", "95617-7", "95616-9", "95615-1"]
    
    async def process_bundle(self, bundle_dict: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Main entry point for processing FHIR bundles
        
        Args:
            bundle_dict: Raw FHIR Bundle as dictionary
            db: Database session
            
        Returns:
            Processing results summary
        """
        processing_id = bundle_dict.get("id", "unknown")
        
        # Create processing log
        log_entry = BundleProcessingLog(
            bundle_id=processing_id,
            processing_id=processing_id,
            status="processing"
        )
        db.add(log_entry)
        db.commit()
        
        try:
            # Validate and parse FHIR bundle
            bundle = Bundle.parse_obj(bundle_dict)
            logger.info(f"Processing FHIR Bundle {bundle.id} with {len(bundle.entry)} entries")
            
            # Extract resources by type
            resources = self._extract_resources_by_type(bundle)
            
            # Process resources in order of dependencies
            member = self._process_member(resources.get("Patient", []), db)
            organization = self._process_organization(resources.get("Organization", []), db)
            encounter = self._process_encounter(resources.get("Encounter", []), member, organization, db)
            consent = self._process_consent(resources.get("Consent", []), member, db)
            
            # Process screening session and responses
            screening_session = self._create_screening_session(bundle, member, encounter, consent, db)
            screening_responses = self._process_observations(resources.get("Observation", []), screening_session, db)
            
            # Calculate safety score and update session
            safety_score = self._calculate_safety_score(screening_responses)
            screening_session.total_safety_score = safety_score
            screening_session.screening_complete = self._is_screening_complete(screening_responses)
            
            # Update processing log
            log_entry.status = "completed"
            log_entry.completed_at = datetime.utcnow()
            log_entry.resources_processed = len(bundle.entry)
            log_entry.members_created = 1 if member else 0
            log_entry.screenings_created = 1 if screening_session else 0
            
            db.commit()
            
            # Return processing summary
            return {
                "status": "success",
                "bundle_id": bundle.id,
                "member_id": str(member.id) if member else None,
                "screening_session_id": str(screening_session.id) if screening_session else None,
                "total_safety_score": safety_score,
                "positive_screens": self._count_positive_screens(screening_responses),
                "resources_processed": len(bundle.entry)
            }
            
        except Exception as e:
            logger.error(f"Error processing bundle {processing_id}: {e}")
            log_entry.status = "failed"
            log_entry.error_message = str(e)
            log_entry.completed_at = datetime.utcnow()
            db.commit()
            raise
    
    def _extract_resources_by_type(self, bundle: Bundle) -> Dict[str, List[Any]]:
        """Extract and group FHIR resources by type"""
        resources = {}
        
        for entry in bundle.entry:
            resource = entry.resource
            resource_type = resource.resourceType
            
            if resource_type not in resources:
                resources[resource_type] = []
            resources[resource_type].append(resource)
        
        return resources
    
    def _process_member(self, fhir_patients: List[FHIRPatient], db: Session) -> Optional[Member]:
        """Process Patient resource and create/update member database record with deduplication"""
        if not fhir_patients:
            return None
        
        fhir_patient = fhir_patients[0]  # Should only be one patient per bundle
        
        # First, try to find existing member by FHIR ID
        existing = db.query(Member).filter(Member.fhir_id == fhir_patient.id).first()
        if existing:
            logger.info(f"Member {fhir_patient.id} already exists, updating...")
            member = existing
        else:
            # Check for potential duplicates using demographic data
            potential_duplicate = self._find_duplicate_member(fhir_patient, db)
            if potential_duplicate:
                logger.info(f"Found potential duplicate member {potential_duplicate.id}, linking FHIR ID {fhir_patient.id}")
                member = potential_duplicate
                # Update FHIR ID to link this bundle to existing member
                member.fhir_id = fhir_patient.id
            else:
                member = Member(fhir_id=fhir_patient.id)
                db.add(member)
        
        # Extract member data
        if fhir_patient.identifier:
            for identifier in fhir_patient.identifier:
                if identifier.type and identifier.type.coding:
                    for coding in identifier.type.coding:
                        if coding.code == "MR":  # Medical Record Number
                            member.mrn = identifier.value
        
        if fhir_patient.name:
            name = fhir_patient.name[0]
            if name.family:
                member.last_name = name.family
            if name.given:
                member.first_name = name.given[0] if name.given else None
        
        member.gender = fhir_patient.gender
        member.date_of_birth = fhir_patient.birthDate
        
        if fhir_patient.address:
            address = fhir_patient.address[0]
            member.address_line1 = address.line[0] if address.line else None
            member.city = address.city
            member.state = address.state
            member.zip_code = address.postalCode
        
        db.commit()
        logger.info(f"Processed member: {member.first_name} {member.last_name}")
        return member
    
    def _process_organization(self, organizations: List[FHIROrganization], db: Session) -> Optional[Organization]:
        """Process Organization resource"""
        if not organizations:
            return None
        
        fhir_org = organizations[0]
        
        # Check if organization exists
        existing = db.query(Organization).filter(Organization.fhir_id == fhir_org.id).first()
        if existing:
            return existing
        
        organization = Organization(fhir_id=fhir_org.id)
        db.add(organization)
        
        organization.name = fhir_org.name
        
        # Map organization type
        if fhir_org.type:
            for org_type in fhir_org.type:
                if org_type.coding:
                    for coding in org_type.coding:
                        organization.organization_type = coding.code
        
        # Extract NPI
        if fhir_org.identifier:
            for identifier in fhir_org.identifier:
                if identifier.type and identifier.type.coding:
                    for coding in identifier.type.coding:
                        if coding.code == "NPI":
                            organization.npi = identifier.value
        
        # Extract address
        if fhir_org.address:
            address = fhir_org.address[0]
            organization.address_line1 = address.line[0] if address.line else None
            organization.city = address.city
            organization.state = address.state
            organization.zip_code = address.postalCode
        
        db.commit()
        logger.info(f"Processed organization: {organization.name}")
        return organization
    
    def _process_encounter(self, encounters: List[FHIREncounter], member: Member, 
                          organization: Organization, db: Session) -> Optional[Encounter]:
        """Process Encounter resource"""
        if not encounters or not member:
            return None
        
        fhir_encounter = encounters[0]
        
        encounter = Encounter(
            fhir_id=fhir_encounter.id,
            member_id=member.id,
            organization_id=organization.id if organization else None,
            status=fhir_encounter.status
        )
        
        # Map encounter type
        if fhir_encounter.type:
            for enc_type in fhir_encounter.type:
                if enc_type.coding:
                    for coding in enc_type.coding:
                        encounter.encounter_type = ENCOUNTER_TYPE_MAPPINGS.get(
                            coding.code, coding.code
                        )
        
        if fhir_encounter.period:
            encounter.encounter_date = fhir_encounter.period.start
        
        db.add(encounter)
        db.commit()
        logger.info(f"Processed encounter: {encounter.fhir_id}")
        return encounter
    
    def _process_consent(self, consents: List[FHIRConsent], member: Member, db: Session) -> bool:
        """Process Consent resource and return consent status"""
        if not consents or not member:
            return False
        
        consent = consents[0]
        return consent.status == "active" and consent.provision and consent.provision.type == "permit"
    
    def _create_screening_session(self, bundle: Bundle, member: Member, 
                                 encounter: Encounter, consent_given: bool, db: Session) -> ScreeningSession:
        """Create screening session record - allows multiple evaluations per member"""
        session = ScreeningSession(
            member_id=member.id,
            encounter_id=encounter.id if encounter else None,
            bundle_id=bundle.id,
            screening_date=datetime.utcnow(),
            consent_given=consent_given
        )
        
        db.add(session)
        db.commit()
        logger.info(f"Created screening session: {session.id}")
        return session
    
    def _process_observations(self, observations: List[FHIRObservation], 
                            screening_session: ScreeningSession, db: Session) -> List[ScreeningResponse]:
        """Process Observation resources (screening Q&A pairs)"""
        responses = []
        
        for obs in observations:
            # Skip non-screening observations (like sexual orientation)
            if not obs.code or not obs.code.coding:
                continue
            
            question_code = None
            for coding in obs.code.coding:
                if coding.code in HRSN_QUESTION_MAPPINGS:
                    question_code = coding.code
                    break
            
            if not question_code:
                continue  # Not an HRSN screening question
            
            response = ScreeningResponse(
                screening_session_id=screening_session.id,
                question_code=question_code
            )
            
            # Get question mapping
            question_mapping = HRSN_QUESTION_MAPPINGS[question_code]
            response.question_text = question_mapping["text"]
            
            # Set SDOH category
            if "category" in question_mapping and question_mapping["category"]:
                response.sdoh_category = question_mapping["category"][0]
            
            # Process answer
            if obs.valueCodeableConcept and obs.valueCodeableConcept.coding:
                answer_coding = obs.valueCodeableConcept.coding[0]
                response.answer_code = answer_coding.code
                response.answer_text = answer_coding.display
                
                # Check if this is a positive screen
                if "positive_answers" in question_mapping:
                    response.positive_screen = answer_coding.code in question_mapping["positive_answers"]
            
            elif obs.valueInteger is not None:
                # Handle safety score total
                response.answer_text = str(obs.valueInteger)
                if question_code == "95614-4":  # Total safety score
                    response.positive_screen = obs.valueInteger >= 11
            
            elif obs.dataAbsentReason:
                # Handle skipped questions
                response.data_absent_reason = obs.dataAbsentReason.coding[0].code if obs.dataAbsentReason.coding else "unknown"
            
            db.add(response)
            responses.append(response)
        
        db.commit()
        logger.info(f"Processed {len(responses)} screening responses")
        return responses
    
    def _calculate_safety_score(self, responses: List[ScreeningResponse]) -> int:
        """Calculate total safety score from questions 9-12"""
        total_score = 0
        
        for response in responses:
            if response.question_code in self.safety_questions and response.answer_code:
                question_mapping = HRSN_QUESTION_MAPPINGS[response.question_code]
                if "score_mapping" in question_mapping:
                    score = question_mapping["score_mapping"].get(response.answer_code, 0)
                    total_score += score
        
        logger.info(f"Calculated safety score: {total_score}")
        return total_score
    
    def _is_screening_complete(self, responses: List[ScreeningResponse]) -> bool:
        """Check if all required screening questions were answered"""
        answered_questions = set()
        
        for response in responses:
            if response.answer_code or response.data_absent_reason:
                answered_questions.add(response.question_code)
        
        # Check for all 12 questions + safety total
        required_questions = set(HRSN_QUESTION_MAPPINGS.keys())
        missing = required_questions - answered_questions
        
        is_complete = len(missing) == 0
        if not is_complete:
            logger.warning(f"Screening incomplete. Missing questions: {missing}")
        
        return is_complete
    
    def _count_positive_screens(self, responses: List[ScreeningResponse]) -> int:
        """Count number of positive screens indicating unmet needs"""
        return sum(1 for r in responses if r.positive_screen)
    
    def _find_duplicate_member(self, fhir_patient: FHIRPatient, db: Session) -> Optional[Member]:
        """
        Find potential duplicate member using demographic matching
        
        Matching criteria:
        1. First name, last name, and date of birth match exactly
        2. OR MRN matches (if available)
        """
        # Extract demographic data from FHIR patient
        first_name = None
        last_name = None
        mrn = None
        
        if fhir_patient.name:
            name = fhir_patient.name[0]
            if name.family:
                last_name = name.family.lower().strip()
            if name.given:
                first_name = name.given[0].lower().strip() if name.given else None
        
        if fhir_patient.identifier:
            for identifier in fhir_patient.identifier:
                if identifier.type and identifier.type.coding:
                    for coding in identifier.type.coding:
                        if coding.code == "MR":  # Medical Record Number
                            mrn = identifier.value
        
        date_of_birth = fhir_patient.birthDate
        
        # Search for duplicates by MRN first (most reliable)
        if mrn:
            duplicate = db.query(Member).filter(Member.mrn == mrn).first()
            if duplicate:
                logger.info(f"Found duplicate member by MRN: {mrn}")
                return duplicate
        
        # Search by demographic data
        if first_name and last_name and date_of_birth:
            # Use case-insensitive matching for names
            duplicate = db.query(Member).filter(
                func.lower(Member.first_name) == first_name,
                func.lower(Member.last_name) == last_name,
                Member.date_of_birth == date_of_birth
            ).first()
            
            if duplicate:
                logger.info(f"Found duplicate member by demographics: {first_name} {last_name} {date_of_birth}")
                return duplicate
        
        return None