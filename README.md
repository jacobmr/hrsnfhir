# HRSN FHIR Processing Server

A comprehensive Health-Related Social Needs (HRSN) FHIR Bundle Processing Server built with FastAPI and PostgreSQL, deployed on Railway. This server processes FHIR bundles containing patient screening data and provides analytics for healthcare organizations.

## 🌐 Live Deployment

**Web Interface**: [https://fhir.sharemy.org/](https://fhir.sharemy.org/)

**API Documentation**: [https://fhir.sharemy.org/docs](https://fhir.sharemy.org/docs)

**Alternative URL**: [https://hrsnfhir-production.up.railway.app/](https://hrsnfhir-production.up.railway.app/)

## ✨ Features

### 🏥 FHIR Bundle Processing
- **Patient/Member Processing**: Extract demographics from FHIR Patient resources
- **Member Deduplication**: Prevent duplicate members using FHIR ID matching
- **Questionnaire Processing**: Process QuestionnaireResponse resources for HRSN screenings
- **Safety Score Calculation**: Automated calculation of safety scores from questions 9-12
- **HRSN Category Support**: Food insecurity, transportation, housing assessments
- **LOINC Code Mapping**: Support for standardized medical coding

### 🗄️ Database Management
- **PostgreSQL Database**: Robust relational database with proper schema
- **Member Management**: Complete member lifecycle with demographics and assessments
- **Screening Sessions**: Track multiple screening sessions per member
- **Response Storage**: Detailed question-answer pairs with scoring
- **Data Integrity**: Foreign key relationships and validation

### 🌐 Web Interface
- **File Upload**: Drag & drop or click to select FHIR JSON bundles
- **Auto-Processing**: Files process automatically upon upload
- **Real-time Processing**: Live feedback during bundle processing
- **Results Display**: Structured display of processed data with clean card-based design
- **Member Browser**: View and search members with assessment history
- **Assessment Details**: Click-through navigation to individual assessment responses
- **CSV Export**: Download member data for analysis
- **Demo Site Warning**: Clear PHI protection messaging for demonstration use
- **Responsive Design**: Works on desktop and mobile devices

### 🔌 REST API
- **OpenAPI Documentation**: Complete API documentation with Swagger UI
- **Authentication**: API key-based security for protected endpoints
- **Member Endpoints**: CRUD operations for member data
- **FHIR Endpoints**: Standards-compliant FHIR bundle submission
- **Health Monitoring**: System health and status endpoints

## 🚀 Quick Start

### Using the Web Interface

1. **Visit the Application**: Go to [https://fhir.sharemy.org/](https://fhir.sharemy.org/)

2. **Upload FHIR Bundle**: 
   - Drag and drop a FHIR JSON file onto the upload area, or
   - Click "Choose File" to select a file from your computer

3. **Process Bundle**: Click "🚀 Process FHIR Bundle" to submit for processing

4. **View Results**: Review the processed member data, screenings, and analytics

5. **Browse Members**: Use the members interface to view individual member details and assessment history

### Using the API

#### Authentication
All protected endpoints require an API key in the Authorization header:
```bash
Authorization: Bearer MookieWilson
```

#### Submit FHIR Bundle
```bash
curl -X POST "https://fhir.sharemy.org/fhir/Bundle" \
  -H "Authorization: Bearer MookieWilson" \
  -H "Content-Type: application/json" \
  -d @your-fhir-bundle.json
```

#### Get Members List
```bash
curl -X GET "https://fhir.sharemy.org/members" \
  -H "Authorization: Bearer MookieWilson"
```

#### Get Member Details
```bash
curl -X GET "https://fhir.sharemy.org/members/{member_id}" \
  -H "Authorization: Bearer MookieWilson"
```

#### Export Members CSV
```bash
curl -X GET "https://fhir.sharemy.org/members/export/csv" \
  -H "Authorization: Bearer MookieWilson" \
  --output members_export.csv
```

## 📚 API Reference

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web interface homepage |
| `GET` | `/health` | System health check |
| `GET` | `/docs` | API documentation |
| `GET` | `/members/count` | Get total member count |
| `POST` | `/api/process-bundle` | Process FHIR bundle (web interface) |

### Protected Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/members` | List all members | ✅ |
| `GET` | `/members/{id}` | Get member details | ✅ |
| `DELETE` | `/members/{id}` | Delete member and data | ✅ |
| `GET` | `/members/export/csv` | Export members to CSV | ✅ |
| `GET` | `/assessments/{id}` | Get assessment details | ✅ |
| `POST` | `/fhir/Bundle` | Submit FHIR bundle | ✅ |

## 🏗️ Technical Architecture

### Technology Stack
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Deployment**: Railway
- **ORM**: SQLAlchemy
- **Authentication**: API Key with HTTPBearer
- **Documentation**: OpenAPI/Swagger

### Database Schema

#### Members Table
```sql
members (
  id UUID PRIMARY KEY,
  fhir_id VARCHAR(64) UNIQUE,
  mrn VARCHAR(50),
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  date_of_birth TIMESTAMP,
  gender VARCHAR(20),
  address VARCHAR(500),
  address_line1 VARCHAR(200),
  city VARCHAR(100),
  state VARCHAR(2),
  zip_code VARCHAR(10),
  phone VARCHAR(20),
  created_at TIMESTAMP
)
```

#### Screening Sessions Table
```sql
screening_sessions (
  id UUID PRIMARY KEY,
  member_id UUID FOREIGN KEY,
  bundle_id VARCHAR(64),
  fhir_questionnaire_response_id VARCHAR(64),
  screening_date TIMESTAMP,
  consent_given BOOLEAN,
  screening_complete BOOLEAN,
  total_safety_score INTEGER,
  positive_screens_count INTEGER,
  questions_answered INTEGER,
  created_at TIMESTAMP
)
```

#### Screening Responses Table
```sql
screening_responses (
  id UUID PRIMARY KEY,
  screening_session_id UUID FOREIGN KEY,
  question_code VARCHAR(20),
  question_text VARCHAR(500),
  answer_code VARCHAR(20),
  answer_text VARCHAR(200),
  sdoh_category VARCHAR(50),
  positive_screen BOOLEAN,
  data_absent_reason VARCHAR(50),
  created_at TIMESTAMP
)
```

## 🔧 FHIR Bundle Processing

### Supported FHIR Resources

#### Patient Resources
- **Extraction**: Demographics, contact information, identifiers
- **Deduplication**: Automatic detection and prevention of duplicate members
- **Validation**: FHIR ID requirements and structure validation

#### QuestionnaireResponse Resources
- **Question Processing**: Support for LOINC-coded questions
- **Answer Types**: valueCoding, valueString, valueBoolean, valueInteger
- **Safety Scoring**: Automated calculation for questions 9-12
- **Category Mapping**: HRSN categories (food, housing, transportation, safety)

### HRSN Question Support

#### Safety Questions (Questions 9-12)
- **95618-5**: Physical hurt frequency
- **95617-7**: Insult/talk down frequency  
- **95616-9**: Threat frequency
- **95615-1**: Scream/curse frequency

**Scoring Scale**: Never (1) → Rarely (2) → Sometimes (3) → Fairly Often (4) → Frequently (5)

#### Social Determinants Questions
- **88122-7**: Food worry (12 months)
- **88123-5**: Food didn't last (12 months)
- **93030-5**: Transportation barriers

### Processing Workflow

1. **Bundle Validation**: Verify FHIR Bundle structure and required fields
2. **Resource Extraction**: Parse Patient and QuestionnaireResponse resources
3. **Member Processing**: Create or update member records with deduplication
4. **Screening Processing**: Create screening sessions and individual responses
5. **Score Calculation**: Calculate safety scores and positive screen counts
6. **Database Storage**: Persist all processed data with relationships
7. **Response Generation**: Return processing results and analytics

## 🚀 Deployment

### Railway Deployment

The application is deployed on Railway with:
- **PostgreSQL Database**: Managed database service
- **Automatic Deployments**: Connected to GitHub for CI/CD
- **Environment Variables**: Secure configuration management
- **Custom Domain**: Production-ready URL

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `DEFAULT_API_KEY` | API authentication key | ✅ |
| `PORT` | Application port (auto-set by Railway) | ✅ |

## 🔒 Security

### Authentication
- **API Key Authentication**: HTTPBearer token-based authentication
- **Protected Endpoints**: Member data and FHIR submission require authentication
- **Public Endpoints**: Health check and documentation remain open

### Data Protection
- **Database Security**: PostgreSQL with connection encryption
- **Input Validation**: Comprehensive FHIR bundle validation
- **Error Handling**: Secure error responses without data leakage

## 📊 Analytics & Reporting

### Member Analytics
- **Member Count**: Total registered members
- **Age Demographics**: Age distribution analysis
- **Geographic Distribution**: ZIP code mapping
- **Assessment History**: Complete screening timeline per member

### Screening Analytics
- **Safety Scores**: Risk assessment scoring (0-20 scale)
- **High-Risk Identification**: Members with safety scores ≥11
- **Positive Screens**: Count of unmet social needs
- **Completion Rates**: Question response completion tracking

### HRSN Category Analytics
- **Food Insecurity**: Identification and prevalence
- **Housing Issues**: Housing instability and inadequate housing
- **Transportation Barriers**: Transportation-related access issues
- **Safety Concerns**: Interpersonal violence and safety risks

## 🛠️ Development

### Local Development Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/jacobmr/hrsnfhir.git
   cd hrsnfhir
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variables**:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/hrsn_db"
   export DEFAULT_API_KEY="your-api-key"
   ```

4. **Run Application**:
   ```bash
   uvicorn simple_main:app --host 0.0.0.0 --port 8000 --reload
   ```

### File Structure
```
├── simple_main.py          # Main application file
├── app/
│   ├── static/
│   │   ├── index.html      # Web interface
│   │   ├── members.html    # Members browser
│   │   └── member.html     # Individual member view
│   ├── models.py           # Database models (legacy)
│   ├── schemas.py          # Pydantic schemas (legacy)
│   └── config.py           # Configuration (legacy)
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
└── README.md              # This file
```

## 📈 Performance

### Database Performance
- **Connection Pooling**: SQLAlchemy connection management
- **Query Optimization**: Efficient member and screening queries
- **Index Strategy**: Primary keys and foreign key indexes

### API Performance
- **Async Processing**: FastAPI async/await support
- **Response Caching**: Efficient data serialization
- **Error Handling**: Graceful error responses

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Standards
- **Python Style**: Follow PEP 8 guidelines
- **Type Hints**: Use type annotations
- **Documentation**: Document all functions and classes
- **Testing**: Include tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- **API Documentation**: Available at `/docs` endpoint
- **Health Monitoring**: Use `/health` endpoint for system status

### Issues
- **GitHub Issues**: Report bugs and feature requests
- **Health Endpoint**: Monitor system status and database connectivity

### Contact
- **Repository**: [https://github.com/jacobmr/hrsnfhir](https://github.com/jacobmr/hrsnfhir)
- **Live Application**: [https://fhir.sharemy.org/](https://fhir.sharemy.org/)

---

## 🔄 Recent Updates

### Latest Version (v1.0.3)
- ✅ Full FHIR bundle processing capability
- ✅ Complete database integration with PostgreSQL
- ✅ Member deduplication and management
- ✅ Safety score calculation and analytics
- ✅ Web interface for file upload and processing
- ✅ REST API with OpenAPI documentation
- ✅ Railway deployment with managed database
- ✅ Authentication and security implementation

**Status**: Production Ready 🚀

The HRSN FHIR Processing Server is fully operational and ready to process healthcare screening data for health-related social needs assessment and analytics.

