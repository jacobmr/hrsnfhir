# app/models.py
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fhir_id = Column(String(64), unique=True, nullable=False)
    mrn = Column(String(50))
    first_name = Column(String(100))
    last_name = Column(String(100))
    date_of_birth = Column(DateTime)
    gender = Column(String(20))
    sexual_orientation = Column(String(50))
    address_line1 = Column(String(200))
    city = Column(String(100))
    state = Column(String(2))
    zip_code = Column(String(10))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    screening_sessions = relationship("ScreeningSession", back_populates="patient")
    eligibility_assessments = relationship("EligibilityAssessment", back_populates="patient")
    service_referrals = relationship("ServiceReferral", back_populates="patient")

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fhir_id = Column(String(64), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    organization_type = Column(String(50))  # 'Other' for SCN Lead, 'Cg' for HRSN Provider
    npi = Column(String(10))
    address_line1 = Column(String(200))
    city = Column(String(100))
    state = Column(String(2))
    zip_code = Column(String(10))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    encounters = relationship("Encounter", back_populates="organization")
    referring_referrals = relationship("ServiceReferral", foreign_keys="ServiceReferral.referring_organization_id", back_populates="referring_organization")
    receiving_referrals = relationship("ServiceReferral", foreign_keys="ServiceReferral.receiving_organization_id", back_populates="receiving_organization")

class Encounter(Base):
    __tablename__ = "encounters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fhir_id = Column(String(64), unique=True, nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    encounter_type = Column(String(50))  # 'direct-questioning' or 'self-administered'
    encounter_date = Column(DateTime)
    status = Column(String(20))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    patient = relationship("Patient")
    organization = relationship("Organization", back_populates="encounters")
    screening_sessions = relationship("ScreeningSession", back_populates="encounter")

class ScreeningSession(Base):
    __tablename__ = "screening_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"), nullable=False)
    bundle_id = Column(String(64))
    screening_date = Column(DateTime)
    consent_given = Column(Boolean)
    screening_complete = Column(Boolean)
    total_safety_score = Column(Integer)  # Sum of questions 9-12
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="screening_sessions")
    encounter = relationship("Encounter", back_populates="screening_sessions")
    responses = relationship("ScreeningResponse", back_populates="screening_session")
    eligibility_assessments = relationship("EligibilityAssessment", back_populates="screening_session")

class ScreeningResponse(Base):
    __tablename__ = "screening_responses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    screening_session_id = Column(UUID(as_uuid=True), ForeignKey("screening_sessions.id"), nullable=False)
    question_code = Column(String(20))  # LOINC code (e.g., '71802-3')
    question_text = Column(Text)
    answer_code = Column(String(20))   # Answer LOINC code
    answer_text = Column(String(200))
    sdoh_category = Column(String(50)) # 'housing-instability', 'food-insecurity', etc.
    positive_screen = Column(Boolean)  # True if indicates unmet need
    data_absent_reason = Column(String(50)) # If question skipped
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    screening_session = relationship("ScreeningSession", back_populates="responses")

class EligibilityAssessment(Base):
    __tablename__ = "eligibility_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    screening_session_id = Column(UUID(as_uuid=True), ForeignKey("screening_sessions.id"))
    assessment_date = Column(DateTime)
    eligibility_status = Column(String(50))  # 'eligible', 'not-eligible', 'pending'
    enhanced_services_eligible = Column(Boolean)
    assessment_complete = Column(Boolean)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="eligibility_assessments")
    screening_session = relationship("ScreeningSession", back_populates="eligibility_assessments")

class ServiceReferral(Base):
    __tablename__ = "service_referrals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    referring_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    receiving_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    service_category = Column(String(50))  # 'housing', 'nutrition', 'transportation', etc.
    referral_date = Column(DateTime)
    referral_status = Column(String(20))  # 'requested', 'accepted', 'completed', 'cancelled'
    service_request_id = Column(String(64))  # FHIR ServiceRequest ID
    task_id = Column(String(64))            # FHIR Task ID  
    procedure_id = Column(String(64))       # FHIR Procedure ID
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="service_referrals")
    referring_organization = relationship("Organization", foreign_keys=[referring_organization_id], back_populates="referring_referrals")
    receiving_organization = relationship("Organization", foreign_keys=[receiving_organization_id], back_populates="receiving_referrals")

class BundleProcessingLog(Base):
    __tablename__ = "bundle_processing_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bundle_id = Column(String(64), nullable=False)
    processing_id = Column(String(64), unique=True, nullable=False)
    status = Column(String(20))  # 'received', 'processing', 'completed', 'failed'
    error_message = Column(Text)
    resources_processed = Column(Integer, default=0)
    patients_created = Column(Integer, default=0)
    screenings_created = Column(Integer, default=0)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())