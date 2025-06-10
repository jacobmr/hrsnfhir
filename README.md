# HRSN FHIR Processing Server

A FastAPI-based server for processing Health-Related Social Needs (HRSN) FHIR data bundles as part of New York State's 1115 Waiver Amendment program.

## Overview

This system processes FHIR-compliant data bundles containing screening responses, eligibility assessments, and service referrals, transforming them into actionable insights for program administration, quality improvement, and regulatory reporting to the Centers for Medicare & Medicaid Services (CMS).

## Features

- **FHIR Bundle Processing**: Handles screening, assessment, and referral bundles
- **Safety Score Calculation**: Processes 12-question AHC HRSN screening tool
- **Real-time Analytics**: Dashboard and reporting capabilities
- **API-First Design**: RESTful endpoints for all operations
- **Docker Support**: Containerized for easy deployment

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)

### Run with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/jacobmr/hrsnfhir.git
   cd hrsnfhir
   ```

2. Start all services:
   ```bash
   docker-compose up -d
   ```

3. Test the server:
   ```bash
   python3 test_server.py
   ```

4. Access the API documentation:
   - http://localhost:8001/docs (Swagger UI)
   - http://localhost:8001/redoc (ReDoc)

### API Endpoints

- `GET /health` - Health check endpoint
- `GET /` - Root endpoint
- `GET /docs` - API documentation
- `POST /fhir/Bundle` - Submit FHIR bundle for processing (planned)
- `GET /analytics/dashboard` - Dashboard analytics (planned)

## Development

### Project Structure

```
├── app/
│   ├── simple_main.py      # Simple FastAPI application
│   ├── main.py             # Full HRSN processing app (WIP)
│   ├── config.py           # Configuration settings
│   ├── models.py           # Database models
│   ├── schemas.py          # Pydantic schemas
│   ├── database.py         # Database connection
│   ├── fhir_processor.py   # FHIR bundle processing
│   └── analytics.py        # Analytics and reporting
├── docker-compose.yml      # Docker services configuration
├── Dockerfile              # Container build instructions
├── requirements.txt        # Python dependencies
└── test_server.py         # Test script
```

### Current Status

- ✅ Basic FastAPI server running
- ✅ Docker containerization
- ✅ Health check endpoint
- 🚧 FHIR bundle processing (in development)
- 🚧 Database integration (in development)
- 🚧 Analytics dashboard (in development)

## Testing

Run the test suite:

```bash
python3 test_server.py
```

## Configuration

The server uses environment variables for configuration. Key settings:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `DEBUG`: Enable debug mode
- `API_KEY_HEADER`: API key header name
- `DEFAULT_API_KEY`: Default API key for development

## Background

This system supports the NYS Health Equity Reform (NYHER) 1115 Waiver Amendment, addressing healthcare disparities through Enhanced HRSN Services across four key domains:

- **Housing Supports**: Addressing housing instability and homelessness
- **Nutrition**: Ensuring food security and access to healthy foods
- **Transportation**: Removing barriers to healthcare access
- **Care Management**: Coordinating comprehensive social care services

## License

MIT License

## Author

Jacob Reider (jacob@reider.us)
