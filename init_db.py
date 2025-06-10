#!/usr/bin/env python3
"""
Database initialization script for production deployment
"""
import os
import sys
import logging
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from app.database import engine
from app.models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database with required tables"""
    try:
        logger.info("Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Database tables created successfully!")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1 as test")
            logger.info(f"✅ Database connection test successful: {result.fetchone()}")
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    init_database()