#!/usr/bin/env python3
"""
Azure App Service startup script for HRSN FHIR Processing Server
"""
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup environment variables and paths for Azure deployment"""
    
    # Ensure the app directory is in Python path
    app_dir = Path(__file__).parent
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))
    
    # Set default environment variables for Azure
    os.environ.setdefault('PORT', '8000')
    os.environ.setdefault('API_HOST', '0.0.0.0')
    os.environ.setdefault('PYTHONPATH', str(app_dir))
    
    # Azure App Service specific settings
    if 'WEBSITE_HOSTNAME' in os.environ:
        logger.info(f"Running on Azure App Service: {os.environ['WEBSITE_HOSTNAME']}")
        # Production settings
        os.environ.setdefault('DEBUG', 'False')
        os.environ.setdefault('LOG_LEVEL', 'INFO')
    else:
        logger.info("Running in local/development environment")
        os.environ.setdefault('DEBUG', 'True')
        os.environ.setdefault('LOG_LEVEL', 'DEBUG')

def create_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'temp',
        'app/static'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")

def main():
    """Main startup function"""
    logger.info("Starting HRSN FHIR Processing Server...")
    
    setup_environment()
    create_directories()
    
    # Import and run the application
    try:
        from app.main import app
        import uvicorn
        
        # Get configuration from environment
        host = os.environ.get('API_HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 8000))
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        logger.info(f"Starting server on {host}:{port} (debug={debug})")
        
        # Start the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            reload=False  # Never reload in production
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()