# Business Requirements Document
## New York State Health-Related Social Needs (HRSN) FHIR Data Processing System

**Document Version:** 1.0  
**Date:** June 9, 2025  
**Prepared for:** New York State Department of Health (NYS DOH)  
**Prepared by:** HRSN Implementation Team  

---

## Executive Summary

The New York State Health-Related Social Needs (HRSN) FHIR Data Processing System is a critical infrastructure component supporting the NYS Health Equity Reform (NYHER) 1115 Waiver Amendment. This system will standardize the collection, processing, and analysis of health-related social needs data across New York State's Social Care Networks (SCNs), enabling effective tracking of Enhanced HRSN Services and supporting data-driven decision making for vulnerable Medicaid populations.

The system processes FHIR-compliant data bundles containing screening responses, eligibility assessments, and service referrals, transforming them into actionable insights for program administration, quality improvement, and regulatory reporting to the Centers for Medicare & Medicaid Services (CMS).

**Key Business Value:**
- Standardized HRSN data collection across 62 counties in New York State
- Real-time monitoring of Enhanced HRSN Services delivery
- Compliance with federal FHIR interoperability requirements
- Data-driven insights for addressing health disparities
- Streamlined reporting to CMS for waiver compliance

---

## Business Context and Background

### 1115 Waiver Program Overview

The NYS Health Equity Reform (NYHER) 1115 Waiver Amendment, approved by CMS on January 9, 2024, addresses healthcare disparities exacerbated by the COVID-19 pandemic. The Social Care Network (SCN) component provides funding for Enhanced HRSN Services targeting eligible Medicaid members across four key domains:

- **Housing Supports:** Addressing housing instability and homelessness
- **Nutrition:** Ensuring food security and access to healthy foods  
- **Transportation:** Removing barriers to healthcare access and daily living
- **Care Management:** Coordinating comprehensive social care services

### Current State Challenges

1. **Data Fragmentation:** HRSN data scattered across multiple systems and organizations
2. **Lack of Standardization:** Inconsistent data collection and reporting formats
3. **Limited Interoperability:** Difficulty sharing data between SCNs and state systems
4. **Manual Processes:** Time-intensive manual reporting and data aggregation
5. **Compliance Risk:** Challenges meeting federal FHIR requirements and CMS reporting

### Regulatory Requirements

- **CMS 1115 Waiver Compliance:** Adherence to federal waiver terms and reporting requirements
- **FHIR R4 Standard:** Implementation of HL7 FHIR R4 for interoperability
- **HIPAA Compliance:** Protection of protected health information (PHI)
- **NYS Privacy Laws:** Compliance with state-specific privacy regulations
- **Quality Measures:** Support for CMS quality reporting requirements

---

## Business Objectives and Goals

### Primary Objectives

1. **Standardize HRSN Data Collection**
   - Implement uniform 12-question AHC HRSN Screening Tool statewide
   - Ensure consistent data quality and completeness across all SCNs
   - Support standardized eligibility assessment processes

2. **Enable Real-Time Program Monitoring**
   - Provide dashboard analytics for program administrators
   - Support real-time tracking of Enhanced HRSN Services delivery
   - Enable early identification of high-risk populations

3. **Ensure Regulatory Compliance**
   - Meet federal FHIR interoperability requirements by October 31, 2024
   - Support CMS reporting requirements for 1115 Waiver
   - Maintain HIPAA compliance for all data processing

4. **Improve Care Coordination**
   - Facilitate data sharing between SCN Lead Entities and HRSN service providers
   - Support referral tracking and outcome measurement
   - Enable care plan coordination across multiple providers

### Secondary Objectives

1. **Support Quality Improvement**
   - Provide analytics for identifying service gaps and opportunities
   - Enable outcome measurement and program evaluation
   - Support evidence-based program modifications

2. **Reduce Administrative Burden**
   - Automate data collection and aggregation processes
   - Streamline reporting workflows for SCN partners
   - Minimize manual data entry and processing

3. **Enable Data-Driven Decision Making**
   - Provide actionable insights for program administration
   - Support resource allocation decisions
   - Enable identification of best practices and successful interventions

---

## Stakeholder Analysis

### Primary Stakeholders

| Stakeholder | Role | Key Interests |
|-------------|------|---------------|
| **NYS Department of Health (DOH)** | Program Administrator | Waiver compliance, program oversight, CMS reporting |
| **Office of Health Insurance Programs (OHIP)** | Medicaid Administrator | Fiscal management, member outcomes, quality measures |
| **SCN Lead Entities** | Program Implementers | Data submission, member management, service coordination |
| **HRSN Service Providers** | Service Delivery | Referral management, outcome tracking, care coordination |
| **Qualified Entities (QEs)** | Data Intermediaries | FHIR data exchange, SHIN-NY integration |
| **CMS** | Federal Oversight | Waiver compliance, quality reporting, program evaluation |

### Secondary Stakeholders

| Stakeholder | Role | Key Interests |
|-------------|------|---------------|
| **Medicaid Members** | Program Beneficiaries | Service access, privacy protection, care quality |
| **Healthcare Providers** | Clinical Partners | Patient outcomes, care coordination, data integration |
| **Community-Based Organizations** | Service Partners | Resource allocation, service delivery, outcome measurement |
| **SHIN-NY Data Lake** | Data Repository | Data standardization, interoperability, analytics |

---

## Functional Requirements

### Core System Functions

#### 1. FHIR Bundle Processing

**FR-001: Bundle Ingestion**
- System SHALL accept FHIR R4 Bundle resources via RESTful API
- System SHALL validate bundle structure against FHIR R4 specifications
- System SHALL support both JSON and XML bundle formats
- System SHALL provide immediate acknowledgment of bundle receipt

**FR-002: Data Validation**
- System SHALL validate all FHIR resources against NY HRSN Implementation Guide v1.4.5
- System SHALL verify presence of required data elements per minimum viable dataset
- System SHALL flag missing or invalid data elements for review
- System SHALL support configurable validation rules

**FR-003: HRSN Screening Processing**
- System SHALL process all 12 questions from AHC HRSN Screening Tool
- System SHALL calculate total safety score from questions 9-12
- System SHALL identify positive screens indicating unmet social needs
- System SHALL handle skipped questions using FHIR dataAbsentReason

#### 2. Data Management

**FR-004: Patient Management**
- System SHALL create and maintain patient records with demographic information
- System SHALL support patient matching and deduplication
- System SHALL maintain patient privacy and access controls
- System SHALL support patient consent management

**FR-005: Screening Session Management**
- System SHALL track complete screening sessions with timestamps
- System SHALL maintain relationship between screening questions and responses
- System SHALL calculate screening completion rates
- System SHALL support multiple screenings per patient over time

**FR-006: Organization Management**
- System SHALL distinguish between SCN Lead Entities and HRSN Service Providers
- System SHALL maintain organization demographics and contact information
- System SHALL support organization hierarchy and relationships
- System SHALL track organization performance metrics

#### 3. Analytics and Reporting

**FR-007: Dashboard Analytics**
- System SHALL provide real-time dashboard with key performance indicators
- System SHALL display screening volumes, completion rates, and positive screen rates
- System SHALL show safety score distributions and high-risk populations
- System SHALL support filtering by organization, time period, and geography

**FR-008: Clinical Decision Support**
- System SHALL identify patients with safety scores ≥11 for priority intervention
- System SHALL categorize unmet needs by SDOH domains
- System SHALL support care gap identification and outreach list generation
- System SHALL provide patient-level screening history and trends

**FR-009: Regulatory Reporting**
- System SHALL generate standardized reports for CMS waiver compliance
- System SHALL support ad-hoc reporting and data exports
- System SHALL maintain audit trails for all data access and modifications
- System SHALL support quality measure calculation and reporting

#### 4. Integration and Interoperability

**FR-010: SHIN-NY Integration**
- System SHALL integrate with SHIN-NY Data Lake for statewide data sharing
- System SHALL support bidirectional data exchange with Qualified Entities
- System SHALL maintain data synchronization and consistency
- System SHALL support real-time and batch data transmission

**FR-011: API Management**
- System SHALL provide RESTful APIs for all major functions
- System SHALL implement proper authentication and authorization
- System SHALL support API versioning and backward compatibility
- System SHALL provide comprehensive API documentation

### Workflow Requirements

#### 1. Screening Workflow

**WF-001: Member Screening Process**
1. Member consents to screening (Question 0)
2. 12-question AHC HRSN screening administered
3. Responses validated and safety score calculated
4. Positive screens flagged for follow-up
5. Screening data transmitted to system via FHIR Bundle

**WF-002: Eligibility Assessment Process**
1. Positive screen triggers eligibility assessment
2. Member contacted for detailed assessment
3. Enhanced Services eligibility determined
4. Assessment results documented and transmitted
5. Care planning initiated for eligible members

**WF-003: Referral Management Process**
1. Service referral created based on assessment
2. HRSN service provider receives referral
3. Member contacted and services initiated
4. Service delivery tracked and outcomes measured
5. Referral closure and outcome reporting

#### 2. Data Flow Requirements

**WF-004: Real-Time Processing**
- FHIR bundles processed within 5 minutes of receipt
- Validation errors reported within 1 minute
- Dashboard updates within 15 minutes of data processing
- Critical alerts (safety scores ≥11) generated immediately

**WF-005: Batch Processing**
- Support for bulk data loads during off-peak hours
- Automated data quality reports generated daily
- Monthly aggregated reports for program administration
- Quarterly compliance reports for CMS submission

---

## Non-Functional Requirements

### Performance Requirements

**NFR-001: Scalability**
- System SHALL support processing of 10,000+ FHIR bundles per day
- System SHALL support 500+ concurrent users
- System SHALL scale horizontally to meet growing demand
- Database SHALL support 100M+ records with sub-second query response

**NFR-002: Availability**
- System SHALL maintain 99.9% uptime during business hours
- System SHALL support planned maintenance windows with 24-hour notice
- System SHALL implement automated failover and disaster recovery
- Data backups SHALL be performed daily with 30-day retention

**NFR-003: Response Time**
- API endpoints SHALL respond within 2 seconds for 95% of requests
- Dashboard pages SHALL load within 3 seconds
- Reports SHALL generate within 30 seconds for standard queries
- Large data exports SHALL complete within 5 minutes

### Security Requirements

**NFR-004: Authentication and Authorization**
- System SHALL implement multi-factor authentication for all users
- System SHALL support role-based access control (RBAC)
- System SHALL integrate with organizational directory services
- API access SHALL require secure token-based authentication

**NFR-005: Data Protection**
- All PHI SHALL be encrypted at rest using AES-256 encryption
- All data transmission SHALL use TLS 1.3 or higher
- System SHALL implement comprehensive audit logging
- Data retention SHALL comply with HIPAA and state requirements

**NFR-006: Privacy and Compliance**
- System SHALL implement HIPAA minimum necessary standard
- System SHALL support data subject rights under applicable privacy laws
- System SHALL provide data lineage and provenance tracking
- System SHALL support automated compliance reporting

### Technical Requirements

**NFR-007: Interoperability**
- System SHALL implement HL7 FHIR R4 standard
- System SHALL support SMART on FHIR security framework
- System SHALL comply with 21st Century Cures Act requirements
- System SHALL support standard terminologies (LOINC, SNOMED CT)

**NFR-008: Data Quality**
- System SHALL implement automated data quality checks
- Data completeness SHALL exceed 95% for required fields
- Data accuracy SHALL be validated through business rules
- System SHALL support data quality monitoring and alerting

---

## Success Criteria and Key Performance Indicators

### Business Success Metrics

| Metric | Target | Measurement Frequency |
|--------|--------|--------------------|
| **SCN FHIR Compliance Rate** | 100% of SCNs FHIR-enabled by 10/31/2024 | Monthly |
| **Screening Volume** | 50,000+ screenings annually | Monthly |
| **Data Completeness** | >95% for required data elements | Weekly |
| **High-Risk Identification** | 100% of safety scores ≥11 flagged within 24 hours | Daily |
| **Referral Tracking** | >90% of referrals tracked to completion | Monthly |

### Technical Success Metrics

| Metric | Target | Measurement Frequency |
|--------|--------|--------------------|
| **System Uptime** | 99.9% availability | Continuous |
| **API Response Time** | <2 seconds 95th percentile | Continuous |
| **Data Processing Speed** | <5 minutes bundle-to-dashboard | Continuous |
| **Error Rate** | <1% validation errors | Daily |
| **Security Incidents** | Zero PHI breaches | Continuous |

### Quality Metrics

| Metric | Target | Measurement Frequency |
|--------|--------|--------------------|
| **User Satisfaction** | >4.0/5.0 rating | Quarterly |
| **Data Accuracy** | >99% validated responses | Monthly |
| **Training Effectiveness** | >90% user competency | Quarterly |
| **Support Response** | <4 hours for critical issues | Continuous |

---

## Implementation Phases and Timeline

### Phase 1: Foundation (Months 1-3)
**Deliverables:**
- Core FHIR processing engine
- Database schema and data models
- Basic validation and business rules
- Development and testing environments

**Success Criteria:**
- Process all three bundle types (screening, assessment, referral)
- Validate against NY HRSN IG v1.4.5
- Support 12-question screener with safety scoring
- Basic API endpoints operational

### Phase 2: Integration (Months 4-6)
**Deliverables:**
- SHIN-NY Data Lake integration
- Qualified Entity API connections
- Authentication and security framework
- Production environment deployment

**Success Criteria:**
- Bidirectional data exchange with SHIN-NY
- Secure API access for all stakeholder types
- Production-ready security and compliance
- Initial SCN pilot deployments

### Phase 3: Analytics and Reporting (Months 7-9)
**Deliverables:**
- Real-time analytics dashboard
- Standard and ad-hoc reporting capabilities
- Care gap identification and alerting
- Quality measure calculation

**Success Criteria:**
- Dashboard accessible to all stakeholder types
- CMS-compliant reporting capabilities
- Automated quality monitoring
- Performance optimization complete

### Phase 4: Full Deployment (Months 10-12)
**Deliverables:**
- Statewide SCN deployment
- Comprehensive user training
- Full operational support
- Performance optimization

**Success Criteria:**
- All SCNs FHIR-enabled and processing data
- Target performance metrics achieved
- Full regulatory compliance demonstrated
- Sustainable operations established

---

## Risk Assessment and Mitigation

### High-Risk Items

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|-------------------|
| **SCN Non-Compliance with FHIR** | High | Medium | Mandatory training, technical assistance, phased implementation |
| **Data Quality Issues** | High | Medium | Automated validation, quality monitoring, feedback loops |
| **Security Breach** | High | Low | Multi-layered security, regular audits, incident response plan |
| **SHIN-NY Integration Delays** | Medium | Medium | Early coordination, technical working groups, fallback options |
| **CMS Reporting Non-Compliance** | High | Low | Regular compliance reviews, mock audits, external validation |

### Medium-Risk Items

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|-------------------|
| **Performance Degradation** | Medium | Medium | Load testing, performance monitoring, scalability planning |
| **User Adoption Challenges** | Medium | Medium | Change management, training programs, support resources |
| **Vendor Dependency** | Medium | Low | Multi-vendor strategy, open standards, contingency planning |
| **Budget Overruns** | Medium | Low | Regular budget reviews, scope management, change control |

### Assumptions and Dependencies

**Key Assumptions:**
- SCN IT platforms will achieve FHIR capability within required timeframes
- Qualified Entities will support necessary data exchange protocols
- SHIN-NY Data Lake will maintain required uptime and performance
- Adequate network connectivity exists across all participating organizations

**Critical Dependencies:**
- NY HRSN Implementation Guide v1.4.5 finalization and adoption
- SHIN-NY Data Lake technical specifications and API availability
- SCN Lead Entity contract execution and technical capability development
- Federal and state funding availability for full implementation

---

## Governance and Change Management

### Project Governance Structure

**Executive Sponsor:** NYS DOH Commissioner  
**Program Manager:** OHIP Assistant Director  
**Technical Lead:** SHIN-NY Technical Director  
**Business Lead:** HRSN Program Director  

**Steering Committee:**
- NYS DOH leadership
- OHIP program management
- SCN Lead Entity representatives
- Qualified Entity technical leads
- External subject matter experts

### Change Control Process

1. **Change Request Submission:** Formal documentation of proposed changes
2. **Impact Assessment:** Technical, business, and financial impact analysis
3. **Stakeholder Review:** Review by affected stakeholder groups
4. **Steering Committee Approval:** Formal approval by governance committee
5. **Implementation Planning:** Detailed implementation and communication plan
6. **Change Implementation:** Controlled rollout with monitoring and validation

### Communication Plan

**Internal Communications:**
- Weekly technical team meetings
- Bi-weekly stakeholder updates
- Monthly steering committee reports
- Quarterly executive briefings

**External Communications:**
- Monthly SCN partner calls
- Quarterly public progress reports
- Annual program evaluation reports
- CMS reporting per waiver requirements

---

## Budget and Resource Requirements

### Technology Infrastructure

| Component | Year 1 Cost | Annual Operating Cost |
|-----------|-------------|---------------------|
| **Cloud Infrastructure** | $150,000 | $200,000 |
| **Database Licensing** | $75,000 | $100,000 |
| **Security Tools** | $50,000 | $75,000 |
| **Monitoring/Analytics** | $40,000 | $60,000 |
| **Integration Platforms** | $100,000 | $125,000 |

### Human Resources

| Role | FTE | Annual Cost |
|------|-----|-------------|
| **Technical Lead** | 1.0 | $150,000 |
| **FHIR Developers** | 3.0 | $360,000 |
| **Database Administrators** | 2.0 | $200,000 |
| **Quality Assurance** | 2.0 | $160,000 |
| **Business Analysts** | 2.0 | $180,000 |
| **Project Management** | 1.0 | $120,000 |

### Total Program Investment

- **Year 1 Implementation:** $1,785,000
- **Annual Operating Cost:** $1,730,000
- **3-Year Total Cost of Ownership:** $5,245,000

### Return on Investment

**Quantified Benefits:**
- Reduced manual reporting effort: $500,000 annually
- Improved care coordination efficiency: $300,000 annually
- Enhanced compliance and reduced risk: $200,000 annually
- **Total Annual Benefits:** $1,000,000

**Payback Period:** 2.1 years  
**3-Year ROI:** 57%

---

## Conclusion

The HRSN FHIR Data Processing System represents a critical investment in New York State's health equity initiative, enabling standardized data collection and analysis across the Social Care Network ecosystem. By implementing this system, NYS will achieve federal compliance requirements while building the data infrastructure necessary for evidence-based program improvements and sustainable health equity outcomes.

The system's modular design and adherence to industry standards ensures scalability and adaptability to evolving program needs, while its comprehensive analytics capabilities will provide unprecedented visibility into HRSN service delivery and member outcomes across the state.

Success of this initiative requires coordinated effort across multiple stakeholder groups, sustained executive commitment, and adequate resource allocation. With proper implementation and ongoing support, this system will serve as a model for other states implementing similar health equity initiatives and contribute to the national advancement of social determinants of health data infrastructure.

---

**Document Approval:**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Business Sponsor | [Name] | _________________ | _________ |
| Technical Lead | [Name] | _________________ | _________ |
| Program Manager | [Name] | _________________ | _________ |
| Quality Assurance | [Name] | _________________ | _________ |

**Next Steps:**
1. Stakeholder review and approval process
2. Detailed technical requirements specification
3. Vendor selection and procurement process
4. Project initiation and team formation