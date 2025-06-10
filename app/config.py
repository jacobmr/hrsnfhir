# app/config.py
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://hrsn_user:secure_password_123@localhost:5432/hrsn_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    API_KEY_HEADER: str = "X-API-Key"
    DEFAULT_API_KEY: str = "hrsn-dev-key-12345"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/hrsn-server.log"
    
    # FHIR Validation
    STRICT_FHIR_VALIDATION: bool = True
    REQUIRE_ALL_SCREENING_QUESTIONS: bool = False  # Allow skipped questions
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# HRSN Question Mappings - Based on NY State 12-question screener
HRSN_QUESTION_MAPPINGS = {
    # Question 1: Living situation
    "71802-3": {
        "text": "What is your living situation today",
        "category": ["housing-instability", "homelessness"],
        "positive_answers": ["LA31994-9", "LA31995-6"]  # Worried about losing it, No steady place
    },
    
    # Question 2: Housing problems
    "96778-6": {
        "text": "Think about the place you live. Do you have problems with any of the following",
        "category": ["inadequate-housing"],
        "positive_answers": ["LA31996-4", "LA28580-1", "LA31997-2", "LA31998-0", "LA31999-8", "LA32000-4", "LA32001-2"]
    },
    
    # Question 3: Utility shutoff
    "96779-4": {
        "text": "In the past 12 months has the electric, gas, oil, or water company threatened to shut off services in your home",
        "category": ["utility-insecurity"],
        "positive_answers": ["LA33-6", "LA32002-0"]  # Yes, Already shut off
    },
    
    # Question 4: Food worry
    "88122-7": {
        "text": "Within the past 12 months, you worried that your food would run out before you got money to buy more",
        "category": ["food-insecurity"],
        "positive_answers": ["LA28397-0", "LA6729-3"]  # Often true, Sometimes true
    },
    
    # Question 5: Food didn't last
    "88123-5": {
        "text": "Within the past 12 months, the food you bought just didn't last and you didn't have money to get more",
        "category": ["food-insecurity"],
        "positive_answers": ["LA28397-0", "LA6729-3"]  # Often true, Sometimes true
    },
    
    # Question 6: Transportation
    "93030-5": {
        "text": "In the past 12 months, has lack of reliable transportation kept you from medical appointments, meetings, work or from getting things needed for daily living",
        "category": ["transportation-insecurity"],
        "positive_answers": ["LA33-6"]  # Yes
    },
    
    # Question 7: Employment
    "96780-2": {
        "text": "Do you want help finding or keeping work or a job",
        "category": ["employment-status"],
        "positive_answers": ["LA31981-6", "LA31982-4"]  # Help finding work, Help keeping work
    },
    
    # Question 8: Education/Training
    "96782-8": {
        "text": "Do you want help with school or training. For example, starting or completing job training or getting a high school diploma, GED or equivalent",
        "category": ["sdoh-category-unspecified"],
        "positive_answers": ["LA33-6"]  # Yes
    },
    
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
    
    # Total Safety Score
    "95614-4": {
        "text": "Total Safety Score",
        "category": ["sdoh-category-unspecified"],
        "is_safety_total": True
    }
}

# Organization type mappings
ORGANIZATION_TYPE_MAPPINGS = {
    "Other": "SCN Lead Entity",
    "Cg": "HRSN Service Provider"
}

# Encounter type mappings
ENCOUNTER_TYPE_MAPPINGS = {
    "23918007": "self-administered",  # History taking, self-administered, by computer terminal
    "405672008": "direct-questioning"  # Direct questioning
}