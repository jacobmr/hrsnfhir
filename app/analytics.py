# app/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from .models import (
    Patient, ScreeningSession, ScreeningResponse, 
    EligibilityAssessment, ServiceReferral, Organization
)
from .schemas import (
    ScreeningSessionSummary, ScreeningResponseSummary,
    EligibilityAssessmentSummary, ServiceReferralSummary,
    PatientSummary, OrganizationSummary
)

def get_patient_screenings(db: Session, patient_id: str) -> List[ScreeningSessionSummary]:
    """Get all screening sessions for a patient"""
    patient = db.query(Patient).filter(Patient.fhir_id == patient_id).first()
    if not patient:
        return []
    
    sessions = db.query(ScreeningSession).filter(
        ScreeningSession.patient_id == patient.id
    ).order_by(desc(ScreeningSession.screening_date)).all()
    
    result = []
    for session in sessions:
        responses = db.query(ScreeningResponse).filter(
            ScreeningResponse.screening_session_id == session.id
        ).all()
        
        response_summaries = [
            ScreeningResponseSummary(
                question_code=r.question_code,
                question_text=r.question_text,
                answer_text=r.answer_text,
                sdoh_category=r.sdoh_category,
                positive_screen=r.positive_screen,
                data_absent_reason=r.data_absent_reason
            ) for r in responses
        ]
        
        positive_count = sum(1 for r in responses if r.positive_screen)
        
        result.append(ScreeningSessionSummary(
            id=str(session.id),
            screening_date=session.screening_date,
            consent_given=session.consent_given,
            screening_complete=session.screening_complete,
            total_safety_score=session.total_safety_score,
            positive_screens_count=positive_count,
            responses=response_summaries
        ))
    
    return result

def get_patient_eligibility_assessments(db: Session, patient_id: str) -> List[EligibilityAssessmentSummary]:
    """Get eligibility assessments for a patient"""
    patient = db.query(Patient).filter(Patient.fhir_id == patient_id).first()
    if not patient:
        return []
    
    assessments = db.query(EligibilityAssessment).filter(
        EligibilityAssessment.patient_id == patient.id
    ).order_by(desc(EligibilityAssessment.assessment_date)).all()
    
    return [
        EligibilityAssessmentSummary(
            id=str(a.id),
            assessment_date=a.assessment_date,
            eligibility_status=a.eligibility_status,
            enhanced_services_eligible=a.enhanced_services_eligible,
            assessment_complete=a.assessment_complete
        ) for a in assessments
    ]

def get_patient_referrals(db: Session, patient_id: str) -> List[ServiceReferralSummary]:
    """Get service referrals for a patient"""
    patient = db.query(Patient).filter(Patient.fhir_id == patient_id).first()
    if not patient:
        return []
    
    referrals = db.query(ServiceReferral).filter(
        ServiceReferral.patient_id == patient.id
    ).order_by(desc(ServiceReferral.referral_date)).all()
    
    result = []
    for referral in referrals:
        referring_org = None
        receiving_org = None
        
        if referral.referring_organization:
            referring_org = OrganizationSummary(
                id=str(referral.referring_organization.id),
                fhir_id=referral.referring_organization.fhir_id,
                name=referral.referring_organization.name,
                organization_type=referral.referring_organization.organization_type,
                city=referral.referring_organization.city,
                state=referral.referring_organization.state
            )
        
        if referral.receiving_organization:
            receiving_org = OrganizationSummary(
                id=str(referral.receiving_organization.id),
                fhir_id=referral.receiving_organization.fhir_id,
                name=referral.receiving_organization.name,
                organization_type=referral.receiving_organization.organization_type,
                city=referral.receiving_organization.city,
                state=referral.receiving_organization.state
            )
        
        result.append(ServiceReferralSummary(
            id=str(referral.id),
            service_category=referral.service_category,
            referral_date=referral.referral_date,
            referral_status=referral.referral_status,
            referring_organization=referring_org,
            receiving_organization=receiving_org
        ))
    
    return result

# app/analytics.py
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta
from collections import Counter
from .models import (
    Patient, ScreeningSession, ScreeningResponse, Organization
)
from .schemas import DashboardAnalytics, SafetyScoreAnalysis, PatientSummary

def generate_dashboard_data(db: Session) -> DashboardAnalytics:
    """Generate dashboard analytics for HRSN data"""
    
    # Basic counts
    total_patients = db.query(Patient).count()
    total_screenings = db.query(ScreeningSession).count()
    
    # Positive screenings (those with at least one positive response)
    positive_screenings = db.query(ScreeningSession).join(ScreeningResponse).filter(
        ScreeningResponse.positive_screen == True
    ).distinct().count()
    
    # High safety risk (safety score >= 11)
    high_safety_risk = db.query(ScreeningSession).filter(
        ScreeningSession.total_safety_score >= 11
    ).count()
    
    # Top unmet needs by SDOH category
    unmet_needs = db.query(
        ScreeningResponse.sdoh_category,
        func.count(ScreeningResponse.id).label('count')
    ).filter(
        ScreeningResponse.positive_screen == True,
        ScreeningResponse.sdoh_category.isnot(None)
    ).group_by(ScreeningResponse.sdoh_category).order_by(desc('count')).limit(5).all()
    
    top_unmet_needs = [
        {"category": need.sdoh_category, "count": need.count}
        for need in unmet_needs
    ]
    
    # Screening completion rate
    completed_screenings = db.query(ScreeningSession).filter(
        ScreeningSession.screening_complete == True
    ).count()
    completion_rate = (completed_screenings / total_screenings * 100) if total_screenings > 0 else 0
    
    # Monthly trends (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_data = db.query(
        extract('year', ScreeningSession.screening_date).label('year'),
        extract('month', ScreeningSession.screening_date).label('month'),
        func.count(ScreeningSession.id).label('count')
    ).filter(
        ScreeningSession.screening_date >= six_months_ago
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    monthly_trends = [
        {
            "month": f"{int(row.year)}-{int(row.month):02d}",
            "screenings": row.count
        }
        for row in monthly_data
    ]
    
    return DashboardAnalytics(
        total_patients=total_patients,
        total_screenings=total_screenings,
        positive_screenings=positive_screenings,
        high_safety_risk_count=high_safety_risk,
        top_unmet_needs=top_unmet_needs,
        screening_completion_rate=round(completion_rate, 1),
        monthly_trends=monthly_trends
    )

def analyze_safety_scores(db: Session) -> SafetyScoreAnalysis:
    """Analyze safety scores across all screenings"""
    
    # Get all screenings with safety scores
    screenings = db.query(ScreeningSession).filter(
        ScreeningSession.total_safety_score.isnot(None)
    ).all()
    
    if not screenings:
        return SafetyScoreAnalysis(
            total_screenings=0,
            average_safety_score=0.0,
            high_risk_count=0,
            score_distribution={},
            high_risk_patients=[]
        )
    
    scores = [s.total_safety_score for s in screenings]
    total_screenings = len(scores)
    average_score = sum(scores) / total_screenings
    high_risk_count = sum(1 for score in scores if score >= 11)
    
    # Score distribution
    score_counter = Counter(scores)
    score_distribution = {str(score): count for score, count in score_counter.items()}
    
    # High risk patients
    high_risk_sessions = [s for s in screenings if s.total_safety_score >= 11]
    high_risk_patients = []
    
    for session in high_risk_sessions[:10]:  # Limit to top 10
        patient = session.patient
        high_risk_patients.append(PatientSummary(
            id=str(patient.id),
            fhir_id=patient.fhir_id,
            first_name=patient.first_name,
            last_name=patient.last_name,
            date_of_birth=patient.date_of_birth,
            gender=patient.gender,
            mrn=patient.mrn
        ))
    
    return SafetyScoreAnalysis(
        total_screenings=total_screenings,
        average_safety_score=round(average_score, 2),
        high_risk_count=high_risk_count,
        score_distribution=score_distribution,
        high_risk_patients=high_risk_patients
    )