# app/analytics_simple.py
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from .models import Member, ScreeningSession, ScreeningResponse

def get_member_screenings(db: Session, member_id: str) -> List[Dict[str, Any]]:
    """Get screening history for a member"""
    screenings = db.query(ScreeningSession).filter(ScreeningSession.member_id == member_id).all()
    
    result = []
    for screening in screenings:
        result.append({
            "id": str(screening.id),
            "screening_date": screening.screening_date.isoformat() if screening.screening_date else None,
            "total_safety_score": screening.total_safety_score,
            "positive_screens_count": screening.positive_screens_count,
            "questions_answered": screening.questions_answered
        })
    
    return result

def get_member_eligibility_assessments(db: Session, member_id: str) -> List[Dict[str, Any]]:
    """Get eligibility assessments for a member"""
    # Placeholder - implement when needed
    return []

def get_member_referrals(db: Session, member_id: str) -> List[Dict[str, Any]]:
    """Get referral history for a member"""
    # Placeholder - implement when needed
    return []

def generate_dashboard_data(db: Session) -> Dict[str, Any]:
    """Generate dashboard analytics for HRSN data"""
    total_members = db.query(Member).count()
    total_screenings = db.query(ScreeningSession).count()
    
    high_risk_screenings = db.query(ScreeningSession).filter(
        ScreeningSession.total_safety_score >= 11
    ).count()
    
    return {
        "total_members": total_members,
        "total_screenings": total_screenings,
        "high_risk_count": high_risk_screenings,
        "positive_screenings": 0,  # Calculate when needed
        "top_unmet_needs": [],
        "screening_completion_rate": 0.0,
        "monthly_trends": []
    }

def analyze_safety_scores(db: Session) -> Dict[str, Any]:
    """Generate safety score analysis report"""
    screenings = db.query(ScreeningSession).filter(
        ScreeningSession.total_safety_score.isnot(None)
    ).all()
    
    if not screenings:
        return {
            "total_screenings": 0,
            "average_safety_score": 0.0,
            "high_risk_count": 0,
            "score_distribution": {},
            "high_risk_members": []
        }
    
    total_score = sum(s.total_safety_score for s in screenings if s.total_safety_score)
    average_score = total_score / len(screenings) if screenings else 0
    high_risk_count = sum(1 for s in screenings if s.total_safety_score and s.total_safety_score >= 11)
    
    return {
        "total_screenings": len(screenings),
        "average_safety_score": round(average_score, 2),
        "high_risk_count": high_risk_count,
        "score_distribution": {},  # Calculate when needed
        "high_risk_members": []
    }