# Business Requirements Document
## MVP Healthcare HRSN FHIR Data Processing System

**Document Version:** 1.0  
**Date:** June 9, 2025  
**Organization:** MVP Healthcare (Medicaid Managed Care Organization)  
**Project Sponsor:** MVP Population Health Leadership  

---

## Executive Summary

MVP Healthcare seeks to implement an internal HRSN FHIR data processing system to receive, process, and analyze health-related social needs screening data for our approximately 180,000 Medicaid members. This system will enable MVP's care management and population health teams to better understand and address the social determinants of health affecting our member population.

**Business Value:**
- Enhanced care management through social needs awareness
- Improved member outcomes and satisfaction
- Proactive identification of high-risk members
- Support for value-based care initiatives
- Compliance with evolving HRSN data sharing requirements

---

## Business Context and Rationale

### Current Challenge

MVP Healthcare currently lacks systematic access to social determinants of health data for our Medicaid members. While Social Care Networks (SCNs) across New York State are conducting HRSN screenings under the 1115 Waiver program, this valuable information remains siloed at the state level, limiting our ability to:

- Provide comprehensive, holistic care management
- Identify members with urgent social needs requiring immediate intervention
- Coordinate care plans that address both medical and social determinants
- Measure and improve outcomes for vulnerable populations

### Business Opportunity

The New York State HRSN data sharing framework creates an opportunity for MVP to access standardized screening data through the following flow:

```
Social Care Networks → NYS DOH → Rochester Rio (QE) → MVP Healthcare
```

By building internal capability to receive and process this FHIR data, MVP will transform from a passive recipient of medical claims to an active participant in comprehensive member health management.

### Strategic Alignment

This initiative aligns with MVP's strategic priorities:
- **Member-Centric Care:** Understanding the full context of member health challenges
- **Population Health Management:** Identifying and addressing community-level health patterns  
- **Value-Based Care:** Supporting quality outcomes and cost management
- **Health Equity:** Addressing disparities through social needs intervention

---

## Business Objectives

### Primary Objectives

1. **Enable Social Needs-Informed Care Management**
   - Provide care managers with complete member social risk profiles
   - Support care plan development that addresses both medical and social needs
   - Enable prioritization of outreach based on screening results

2. **Identify High-Risk Members**
   - Automatically flag members with safety concerns (safety score ≥11)
   - Identify members with multiple unmet social needs requiring urgent intervention
   - Support proactive outreach and resource connection

3. **Support Population Health Analytics**
   - Analyze social needs patterns across MVP's member population
   - Identify geographic and demographic trends in social risk factors
   - Inform population health strategy and resource allocation

4. **Improve Care Coordination**
   - Bridge medical care teams with social care networks
   - Support referral tracking and outcome measurement
   - Enable collaborative care planning across providers

### Success Metrics

| Metric | Target | Timeframe |
|--------|--------|-----------|
| **Data Processing Volume** | Process 100% of member screening data received | Ongoing |
| **High-Risk Identification** | Flag safety scores ≥11 within 24 hours | Daily |
| **Care Manager Adoption** | 80% of care managers accessing HRSN data monthly | 6 months |
| **Member Outreach** | 50% improvement in social needs-based outreach | 12 months |

---

## Functional Requirements

### Core System Capabilities

#### 1. FHIR Data Reception
- **Receive screening data** in FHIR Bundle format from Rochester Rio
- **Validate data integrity** and completeness upon receipt  
- **Process 12-question HRSN screening** responses per NY State standard
- **Handle member matching** to existing MVP member records

#### 2. Data Processing and Storage
- **Extract patient demographics** and match to MVP member database
- **Process screening responses** with question-by-question analysis
- **Calculate safety scores** from screening questions 9-12
- **Identify positive screens** indicating unmet social needs
- **Store data in SQL tables** optimized for care management access

#### 3. Clinical Decision Support
- **Generate high-priority alerts** for members with safety scores ≥11
- **Categorize unmet needs** by domain (housing, food, transportation, etc.)
- **Create care management worklists** based on screening results
- **Support member risk stratification** incorporating social factors

#### 4. Analytics and Reporting
- **Population health dashboard** showing social needs trends
- **Member-level screening history** and longitudinal tracking  
- **Care manager reporting** for caseload management
- **Executive dashboards** for program oversight

---

## Technical Requirements

### System Architecture
- **RESTful API** to receive FHIR bundles from Rochester Rio
- **SQL database** for efficient storage and querying of HRSN data
- **Web-based dashboard** for care manager and analyst access
- **Integration points** with existing MVP systems (EMR, care management platform)

### Data Requirements
- **Member matching** using MVP member IDs and demographics
- **FHIR validation** against NY HRSN Implementation Guide
- **Data retention** per HIPAA and MVP policy requirements
- **Audit logging** for all data access and modifications

### Performance Requirements
- **Process screening data** within 4 hours of receipt
- **Dashboard responsiveness** under 3 seconds for standard queries
- **Support 100+ concurrent users** during business hours
- **99.5% system availability** during core hours (8 AM - 6 PM)

---

## Implementation Approach

### Phase 1: Foundation (Months 1-2)
**Deliverables:**
- FHIR processing server capable of receiving screening bundles
- SQL database schema for HRSN data storage
- Basic validation and member matching logic
- Development environment and testing framework

**Acceptance Criteria:**
- Successfully process sample screening bundles
- Accurately calculate safety scores and identify positive screens
- Match screening data to MVP member records
- Store data in queryable SQL format

### Phase 2: Integration and Analytics (Months 3-4)
**Deliverables:**
- Rochester Rio data connection and authentication
- Care management dashboard with member-level screening data
- High-risk member alerting and prioritization
- Population health reporting capabilities

**Acceptance Criteria:**
- Live data flow from Rochester Rio operational
- Care managers can access member screening results
- Automated alerts for safety scores ≥11 functional
- Population health trends visible in dashboard

### Phase 3: Optimization and Training (Months 5-6)
**Deliverables:**
- Care manager training and workflow integration
- Performance optimization and scalability improvements
- Advanced analytics and trend reporting
- Integration with existing MVP care management systems

**Acceptance Criteria:**
- 80% of care managers trained and using system
- Target performance metrics achieved
- Advanced reporting capabilities operational
- Sustainable operations and support processes

---

## Resource Requirements

### Technology Investment
- **Development Team:** 2 developers, 1 data analyst (6 months)
- **Infrastructure:** Cloud hosting, database licensing, security tools
- **Integration:** Rochester Rio connectivity, MVP system integration

### Operational Requirements  
- **Care Management Training:** HRSN data interpretation and workflow integration
- **IT Support:** Ongoing system maintenance and user support
- **Analytics Team:** Population health reporting and trend analysis

### Estimated Budget
- **Implementation (6 months):** $150,000
- **Annual Operating Cost:** $75,000
- **Training and Change Management:** $25,000

---

## Risk Assessment

### Key Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Data Quality Issues** | Medium | Robust validation, feedback loops with state systems |
| **Low Care Manager Adoption** | High | Comprehensive training, workflow integration, executive support |
| **Rochester Rio Integration Delays** | Medium | Early technical coordination, backup data sources |
| **Member Privacy Concerns** | High | HIPAA compliance, transparent member communication |

---

## Business Case Summary

### Investment Justification

**Quantified Benefits:**
- **Improved Care Efficiency:** Targeted interventions based on social needs data
- **Reduced Emergency Utilization:** Proactive addressing of social determinants  
- **Enhanced Member Satisfaction:** Comprehensive care addressing root causes
- **Value-Based Care Performance:** Better outcomes through holistic care management

**Strategic Benefits:**
- Positions MVP as leader in social determinants-informed care
- Supports health equity initiatives and community partnerships
- Enables data-driven population health management
- Creates foundation for expanded social care integration

### Return on Investment

While difficult to quantify precisely, similar initiatives have shown:
- 10-15% reduction in emergency department utilization
- 20-25% improvement in care plan adherence
- Significant improvement in member satisfaction scores
- Enhanced performance on quality measures and star ratings

For MVP's 180,000 member population, even modest improvements in outcomes and efficiency will justify the investment while positioning the organization for future value-based care success.

---

## Next Steps

1. **Executive Approval:** Secure leadership commitment and budget authorization
2. **Technical Planning:** Detailed system design and architecture planning
3. **Rochester Rio Coordination:** Establish technical connectivity and data sharing agreements
4. **Development Team Formation:** Assemble technical team and project management
5. **Implementation Kickoff:** Begin Phase 1 development and testing

**Target Go-Live Date:** 6 months from project approval

---

**Document Approval:**

| Role | Name | Date |
|------|------|------|
| **VP Population Health** | _________________ | _________ |
| **Chief Medical Officer** | _________________ | _________ |
| **Chief Information Officer** | _________________ | _________ |
| **Project Sponsor** | _________________ | _________ |