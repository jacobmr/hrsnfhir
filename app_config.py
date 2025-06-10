"""
Production configuration override for Azure App Service
"""
import os
from app.config import Settings

class ProductionSettings(Settings):
    """Production-specific settings for Azure deployment"""
    
    # Override development defaults with production values
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Security settings for production
    FORCE_SSL: bool = True
    SECURE_SSL_REDIRECT: bool = True
    
    # Database with SSL required for Azure
    @property
    def DATABASE_URL(self) -> str:
        db_url = os.environ.get('DATABASE_URL')
        if db_url and 'sslmode=' not in db_url:
            # Ensure SSL is enabled for Azure Database for PostgreSQL
            separator = '&' if '?' in db_url else '?'
            db_url += f'{separator}sslmode=require'
        return db_url or super().DATABASE_URL
    
    # CORS settings for production
    @property
    def ALLOWED_ORIGINS(self) -> list:
        origins = os.environ.get('ALLOWED_ORIGINS', '[]')
        try:
            import json
            return json.loads(origins)
        except:
            # Fallback to Azure App Service domain
            hostname = os.environ.get('WEBSITE_HOSTNAME', 'localhost:8000')
            return [f"https://{hostname}"]
    
    # API configuration
    @property
    def API_HOST(self) -> str:
        # Azure App Service binds to 0.0.0.0
        return "0.0.0.0"
    
    @property
    def API_PORT(self) -> int:
        # Azure sets the PORT environment variable
        return int(os.environ.get('PORT', 8000))
    
    # Logging configuration for Azure
    @property
    def LOG_FILE(self) -> str:
        # Use Azure's log directory if available
        if 'WEBSITE_SITE_NAME' in os.environ:
            return f"/home/LogFiles/application/{os.environ['WEBSITE_SITE_NAME']}.log"
        return "logs/hrsn-production.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Use production settings if we're in Azure App Service
if 'WEBSITE_HOSTNAME' in os.environ:
    settings = ProductionSettings()
else:
    from app.config import settings