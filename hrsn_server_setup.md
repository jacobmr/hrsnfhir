# HRSN FHIR Processing Server Setup

## Quick Start on Fresh Linux Box

### Prerequisites
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+, PostgreSQL, Redis
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server git curl

# Install Docker (optional, for containerized deployment)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 1. Project Setup
```bash
# Create project directory
mkdir hrsn-server && cd hrsn-server

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Create project structure
mkdir -p {app,database,config,tests,logs}
```

### 2. Database Setup
```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE hrsn_db;"
sudo -u postgres psql -c "CREATE USER hrsn_user WITH PASSWORD 'secure_password_123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hrsn_db TO hrsn_user;"

# Test connection
psql -h localhost -U hrsn_user -d hrsn_db -c "SELECT version();"
```

### 3. Redis Setup
```bash
# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping  # Should return PONG
```

### 4. Environment Configuration
Create `.env` file:
```bash
cat > .env << EOF
# Database
DATABASE_URL=postgresql://hrsn_user:secure_password_123@localhost:5432/hrsn_db

# Redis
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Security
SECRET_KEY=$(openssl rand -hex 32)
API_KEY_HEADER=X-API-Key
DEFAULT_API_KEY=hrsn-dev-key-$(date +%s)

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/hrsn-server.log
EOF
```

## Installation Commands

### Install Python Dependencies
```bash
# Install core dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic redis celery pydantic
pip install python-multipart python-jose passlib bcrypt python-dotenv

# Install FHIR libraries
pip install fhir.resources pydantic-v1

# Development tools
pip install pytest pytest-asyncio httpx black isort flake8
```

### Generate requirements.txt
```bash
pip freeze > requirements.txt
```

## Docker Alternative (Recommended)

### Docker Compose Setup
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/hrsn
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=hrsn
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  worker:
    build: .
    command: celery -A app.worker worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/hrsn
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Quick Deploy Commands

### Option 1: Direct Python
```bash
# Clone/create project
git clone <your-repo> hrsn-server  # or use the files below
cd hrsn-server

# Setup environment
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Setup database
alembic upgrade head

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Option 2: Docker (Easiest)
```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop everything
docker-compose down
```

## Testing the Server

### Health Check
```bash
curl http://localhost:8000/health
```

### Submit Test Bundle
```bash
# Submit Bundle 1 (High-Risk Member)
curl -X POST http://localhost:8000/fhir/Bundle \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d @bundle_1.json

# Check processing status
curl http://localhost:8000/fhir/Bundle/<bundle-id>
```

### Access Database
```bash
# Connect to database
psql -h localhost -U hrsn_user -d hrsn_db

# Check tables
\dt

# View screening data
SELECT p.first_name, p.last_name, s.screening_date, s.total_safety_score 
FROM patients p 
JOIN screening_sessions s ON p.id = s.patient_id;
```

## Next Steps After Setup

1. **Test with Sample Bundles**: Use the three FHIR bundles I created
2. **Monitor Logs**: Check `logs/hrsn-server.log` for processing details
3. **Database Queries**: Explore the SQL tables for HRSN analytics
4. **API Documentation**: Visit `http://localhost:8000/docs` for interactive API docs
5. **Scale Up**: Add more worker processes for production load

## Security Notes

- Change default passwords in production
- Use proper API key authentication
- Enable HTTPS with SSL certificates
- Configure firewall rules (ports 8000, 5432, 6379)
- Regular database backups