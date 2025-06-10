# app/schemas.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ProcessingStatus(str, Enum):
    RECEIVED = "received"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class BundleResponse(BaseModel):
    bundle_id: str
    processing_id: str
    status: str
    message: str
    received_at: datetime

class BundleProcessingStatus(BaseModel):
    bundle_id: str
    processing_id: str
    status: ProcessingStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    resources_processed: int = 0
    members_created: int = 0
    screenings_created: int = 0

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database: str
    version: str

class MemberSummary(BaseModel):
    id: str
    fhir_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    date_of_birth: Optional[datetime]
    gender: Optional[str]
    mrn: Optional[str]

class ScreeningResponseSummary(BaseModel):
    question_code: str
    question_text: str
    answer_text: Optional[str]
    sdoh_category: Optional[str]
    positive_screen: Optional[bool]
    data_absent_reason: Optional[str]

class ScreeningSessionSummary(BaseModel):
    id: str
    screening_date: datetime
    consent_given: Optional[bool]
    screening_complete: Optional[bool]
    total_safety_score: Optional[int]
    positive_screens_count: int
    responses: List[ScreeningResponseSummary]

class OrganizationSummary(BaseModel):
    id: str
    fhir_id: str
    name: str
    organization_type: Optional[str]
    city: Optional[str]
    state: Optional[str]

class EligibilityAssessmentSummary(BaseModel):
    id: str
    assessment_date: datetime
    eligibility_status: Optional[str]
    enhanced_services_eligible: Optional[bool]
    assessment_complete: Optional[bool]

class ServiceReferralSummary(BaseModel):
    id: str
    service_category: Optional[str]
    referral_date: datetime
    referral_status: Optional[str]
    referring_organization: Optional[OrganizationSummary]
    receiving_organization: Optional[OrganizationSummary]

class DashboardAnalytics(BaseModel):
    total_members: int
    total_screenings: int
    positive_screenings: int
    high_safety_risk_count: int  # Safety score >= 11
    top_unmet_needs: List[Dict[str, Any]]
    screening_completion_rate: float
    monthly_trends: List[Dict[str, Any]]

class SafetyScoreAnalysis(BaseModel):
    total_screenings: int
    average_safety_score: float
    high_risk_count: int  # Score >= 11
    score_distribution: Dict[str, int]
    high_risk_members: List[MemberSummary]