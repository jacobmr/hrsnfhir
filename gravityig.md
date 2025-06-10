# Home - v1.4.5

<script src="assets/js/prism.js"></script><script type="text/javascript" src="assets/js/mermaid.js"></script><script type="text/javascript" src="assets/js/mermaid-init.js"></script><style type="text/css">h2{--heading-prefix:"1"} h3,h4,h5,h6{--heading-prefix:"1"}</style>

  
1.4.5 - release

[FHIR](http://hl7.org/fhir/R4/index.html)

-   [Home](index.html)
-   [Artifacts](#)
    -   [Profiles](artifacts.html#2)
    -   [Extensions](artifacts.html#3)
    -   [Value Sets](artifacts.html#3)
-   [Change Log](change_log.html)
-   [Downloads](downloads.html)
-   [Support](#)
    -   [Public Jira Link](https://nyec.atlassian.net/servicedesk/customer/portal/19)

-   [**Table of Contents**](toc.html)
-   **Home**

<style type="text/css">h2:before{color:silver;counter-increment:section;content:var(--heading-prefix) " ";} h3:before{color:silver;counter-increment:sub-section;content:var(--heading-prefix) "." counter(sub-section) " ";} h4:before{color:silver;counter-increment:composite;content:var(--heading-prefix) "." counter(sub-section) "." counter(composite) " ";} h5:before{color:silver;counter-increment:detail;content:var(--heading-prefix) "." counter(sub-section) "." counter(composite) "." counter(detail) " ";} h6:before{color:silver;counter-increment:more-detail;content:var(--heading-prefix) "." counter(sub-section) "." counter(composite) "." counter(detail) "." counter(more-detail)" ";}</style>

SHINNYHRSN - Local Development build (v1.4.5) built by the FHIR (HL7® FHIR® Standard) Build Tools. See the [Directory of published versions](http://shinny.org/us/ny/hrsn/history.html)

## Home[](#home)

_Official URL_: http://shinny.org/us/ny/hrsn/ImplementationGuide/us.ny.hrsn

_Version_: 1.4.5

Active as of 2025-05-12

_Computable Name_: SHINNYHRSN

-   [1115 SHIN-NY FHIR Implementation Guide](#1115-shin-ny-fhir-implementation-guide)
    -   [Purpose](#purpose)
    -   [Background](#background)
    -   [FHIR Implementation Guide (IG) Use Case](#fhir-implementation-guide-ig-use-case)
    -   [Health-Related Social Needs (HRSN)](#health-related-social-needs-hrsn)
    -   [Social Care Navigation Process](#social-care-navigation-process)
    -   [Social Care Networks](#social-care-networks)
    -   [Statewide Health Information for New York (SHIN-NY)](#statewide-health-information-for-new-york-shin-ny)
    -   [FHIR Bundles](#fhir-bundles)
    -   [Referral Workflow](#referral-workflow)
    -   [Minimum Viable Data Set](#minimum-viable-data-set)

# 1115 SHIN-NY FHIR Implementation Guide

### Purpose[](#purpose)

This 1115 SHIN-NY FHIR Implementation Guide (IG) was created for the exchange of health-related social needs (HRSN) data for New York State’s Health Equity Reform (NYHER) 1115 Waiver Amendment. Specifically, this guide defines Fast Healthcare Interoperability Resource (FHIR) exchange between an organization supporting the Waiver and a Qualified Entity (QE) here in New York State (NYS).

### Background[](#background)

The NYHER 1115 Waiver Amendment was approved by CMS on January 9, 2024. This Waiver provides funding to address disparities in healthcare that were exacerbated by the COVID-19 pandemic.1 Specifically, the SCN component of the Waiver was designed with a statewide vision and regional design for delivery of Enhanced HRSN Services for eligible Medicaid Members.

### FHIR Implementation Guide (IG) Use Case[](#fhir-implementation-guide-ig-use-case)

This IG was developed to support FHIR-enabled information technology (IT) platforms used for this Waiver to the QE.

-   The Social Care Network (SCN) Lead Entity Request for Applications requires each SCN IT Platform to be FHIR enabled within 90 days of contracting (10/31/2024).
-   SCN IT Platforms should be compliant with this IG to be considered FHIR enabled.
-   This IG should be used for all FHIR exchange between the SCN, QEs, and the Statewide Health Information Network for New York (SHIN-NY) Data Lake.
-   This IG was built with the guidance, support, and dependency on the Gravity Project’s Implementation Guide to directly align with national standards wherever possible.

### Health-Related Social Needs (HRSN)[](#health-related-social-needs-hrsn)

The Waiver supports HRSN infrastructure, including the creation of new Social Care Networks, comprised of an SCN Lead Entity and contracted HRSN service providers, and reimbursing for Screening, Navigation, and delivery of Enhanced HRSN Services through the Medicaid program.2

The Waiver will support services for:

**Screening and Navigation:**

-   Fee-for-service (FFS) Members that have a positive HRSN Screening are navigated to existing federal, state, or local resources.
-   Medicaid Managed Care (MMC) Members who screen positive but do not meet eligibility criteria for Enhanced HRSN Services are referred to existing federal, state, or local resources services.

**Enhanced HRSN Services:**

-   MMC Members who screen positive and meet specific clinical criteria in the Eligibility Assessment to be eligible for Enhanced HRSN Services post-screening and assessment are referred to Enhanced HRSN Services delivered within the SCN.3 The Enhanced HRSN Services include:
-   Housing Supports
-   Nutrition
-   Transportation
-   Care Management

Please see the Office of Health Insurance Program’s (OHIP) website for more details on these [Enhanced HRSN Services](https://www.health.ny.gov/health_care/medicaid/redesign/sdh/).

### Social Care Navigation Process[](#social-care-navigation-process)

The pathway to address if a Member has an unmet HRSN starts with 12 questions identified by (NYS) from the Accountable Healthcare Communities (AHC) Health-Related Social Needs (HRSN) Screening Tool. If a Member is Screened positive using the AHC HRSN Screening Tool, they continue to the Eligibility Assessment. An Eligibility Assessment includes working with the Member to confirm their HRSNs; understanding the current services a Member may already be receiving; and discussing additional social risk factors and clinical criteria to understand which HRSN Enhanced Services a Member may be eligible for. This assessment will be based on information provided in the Enhanced Services Member File shared by the MCO and additional information provided by the Member and/or their healthcare provider.

If the Member meets specific criteria, they will be eligible for Enhanced HRSN Services. If the Member does not meet specific criteria, they will receive Navigation to existing federal, state, or local resources. For Navigation to these services, we would expect to see a “ServiceRequest’ but not a closed “Task” (please see below for more details). However, Navigators will be responsible for developing Social Care Plans for eligible Members that include a summary of Member needs, eligibility, and services to which Members are referred.

If a Member is eligible for Enhanced HRSN Services, they are referred to an HRSN service provider in the SCN to deliver appropriate Enhanced HRSN Services. HRSN service providers are entities contracted into the SCN that deliver Enhanced HRSN Services. HRSN service providers include but are not limited to community-based organizations (CBOs), healthcare providers, for-profit organizations, etc. Referrals will be closed after the service is provided by the HRSN service provider.

### Social Care Networks[](#social-care-networks)

An SCN is comprised of an SCN Lead Entity who contracts and coordinates with a network of HRSN service providers, inclusive of CBOs, healthcare providers (inclusive of behavior health and primary care providers), and other organizations providing HRSN services.

SCN Lead Entities will help to develop a local hub in their region for Member outreach and play a vital community role in this waiver.

### Statewide Health Information for New York (SHIN-NY)[](#statewide-health-information-for-new-york-shin-ny)

SCN Lead Entities and HRSN service providers contracted into the Network are required to connect to their local QE in New York to exchange HRSN waiver data. The QE will then send all HRSN data to the SHIN-NY Data Lake, a statewide centralized repository. The SHIN-NY Data Lake can be queried to display Member HRSN data in a QE’s portal. SCN Lead Entities will also receive extracts from the SHIN-NY Data Lake. Ultimately, the SHIN-NY Data Lake repository delivers all HRSN data from the waiver to Medicaid for network and fiscal management.

<style>/*table.style1, tr, th, td {*/ /* border: hidden!important;*/ /* border-collapse: collapse;*/ /* !*background-color: #f9f9f9;*!*/ /* !*hover {background-color: #f9f9f9;}*!*/ /* text-align: center;*/ /* width: 100%;*/ /* margin-left: auto;*/ /* margin-right: auto;*/ /* !*table-layout: auto;*!*/ /*}*/ table.style2, th, td { border: 1px solid; /* width: 85%; */ border-collapse: separate; margin-left: auto; margin-right: auto; text-align: left; /* column-width: auto; */ /*td {*/ /* border-left: 1px solid;*/ /* border-right: 1px solid;*/ /*}*/ } tr:nth-child(even) { background-color: #f2f2f2; } div { column-width: auto; column-gap: 30px; column-rule: 1px double #ff00ff; }</style>

![](WorkflowImage.png)

Artifact 1: 1115 data waiver flow from Member to Medicaid (NYS DOH OHIP)

### FHIR Bundles[](#fhir-bundles)

#### FHIR Workflow[](#fhir-workflow)

![](FHIRWorkflow.png)

Artifact 2: FHIR IG workflow and resources.

#### Screening[](#screening)

The Screening bundle includes the standardized 12 AHC HRSN Screening Tool questions and supporting information. This bundle must include the asterisked items and may include the non-asterisked items.

ResourceType

Purpose

**Bundle\***

Gathers a collection of resources into a single instance with containing context.4

**Consent\***

Represents member consent for the screening (Question 0 on a screening).

**Patient\***

Represents key demographic information needed for Member identification.

**Sexual Orientation Observation\***

Represents information about the Member’s sexual orientation.

**Organization\***

Represents information about the organization where the

screening is performed.

 

**Location\***

Represents the location of the screening encounter.

**Encounter\***

Important for the modality of the episode of care and to identify the encounter it happened in.

**Observation\***

Represents a specific question-answer pair from a Member’s screening questionnaire. All questions from a completed screening questionnaire are required to be represented as Observations.

**Questionnaire**

Represents the screening questionnaire (prior to administration to the Member).

**QuestionnaireResponse**

Represents the screening questionnaire with the answers provided (after administration to the Member).

_\*Required_

#### Assigning Social Determinants of Health (SDOH) Domains/Categories to Obseervations[](#assigning-social-determinants-of-health-sdoh-domainscategories-to-obseervations)

The Table below provides appropriate SDOH Category Code(s) (for Observation.category) for the listed AHC HRSN Screening Tool questions (represented by Observation.code).

Question

SDOH Category Code

Text

What is your living situation today?

housing-instability

Housing Instability

 

homelessness

Homelessness

Think about the place you live. Do you have problems with any of the following?

inadequate-housing

Inadequate Housing

In the past 12 months has the electric, gas, oil, or water company threatened to shut off services in your home?

utility-insecurity

Utility Insecurity

Within the past 12 months, you worried that your food would run out before you got money to buy more.

food-insecurity

Food Insecurity

Within the past 12 months, the food you bought just didn't last and you didn't have money to get more.

food-insecurity

Food Insecurity

In the past 12 months, has lack of reliable transportation kept you from medical appointments, meetings, work or from getting things needed for daily living?

transportation-insecurity

Transportation Insecurity

Do you want help finding or keeping work or a job?

employment-status

Employment Status

Do you want help with school or training? For example, starting or completing job training or getting a high school diploma, GED or equivalent.

sdoh-category-unspecified

Education/Training

How often does anyone, including family and friends, physically hurt you?

sdoh-category-unspecified

Interpersonal Safety

How often does anyone, including family and friends, insult or talk down to you?

sdoh-category-unspecified

Interpersonal Safety

How often does anyone, including family and friends, threaten you with harm?

sdoh-category-unspecified

Interpersonal Safety

How often does anyone, including family and friends, scream or curse at you?

sdoh-category-unspecified

Interpersonal Safety

Safety Score

sdoh-category-unspecified

Interpersonal Safety

#### Local Panel Code for New York State’s AHC HRSN Screening Tool[](#local-panel-code-for-new-york-states-ahc-hrsn-screening-tool)

Since New York State’s 12 question screener uses all the AHC HRSN Screening Tool Core Questions and only two of the AHC HRSN Screening Tool Supplemental Questions, there is no code in LOINC to represent the local NYS version of the AHC HRSN Screening Tool. Therefore, NYS will be using the local code below.

SCREENING\_PARENT\_CODE

SCREENING\_CODE\_DESCRIPTION

NYSAHCHRSN

NYS Accountable Health Communities (AHC) Health-Related Social Needs (HRSN) Screening Tool

#### Observation Interpretation[](#observation-interpretation)

In the Observation Screening Response profile, the Observation.interpretation element can be used to flag Observations that might represent a health-related social need (HRSN). (For additional guidance on the use of Observation.interpretation: [POS](https://hl7.org/fhir/R4/v3/ObservationInterpretation/cs.html#v3-ObservationInterpretation-POS) (Positive) to flag Observations for which the Q-A pair might represent a HRSN, see ["Flagging Observations for possible HRSN need using Observation.interpreation"](https://build.fhir.org/ig/HL7/fhir-sdoh-clinicalcare/assessment_instrument_support.html#flagging-observations-for-a-possible-hrsn-need-using-observationinterpretation) in the [SDOH Clinical Care Implementation Guide](https://hl7.org/fhir/us/sdoh-clinicalcare/).)

The attribution, Observation interpretation, within an Observation Screening Response resource type shows a possible unmet need. For [AHC HRSN this is defined as any underlined answers shown on their screening](https://www.cms.gov/priorities/innovation/files/worksheets/ahcm-screeningtool.pdf).

Citations for all screening questions found here (https://www.cms.gov/priorities/innovation/media/document/ahcm-screening-tool-citation)

All **bolded ANSWER\_DISPLAY** values show a possible unmet need.

QUESTION\_TEXT and QUESTION\_CODE

ANSWER\_DISPLAY

ANSWER\_CODE

CITATION

1\. What is your living situation today?\*(71802-3)

I have a steady place to live

LA31993-1

National Association of Community Health Centers and Partners, National Association of Community Health Centers, Association of Asian Pacific Community Health Organizations, Association OPC, Institute for Alternative Futures. (2017). PRAPARE. http://www.nachc.org/research-and-data/prapare/

 

**I have a place to live today, but I am worried about losing it in the future**

LA31994-9

 

 

**I do not have a steady place to live (I am temporarily staying with others, in a hotel, in a shelter, living outside on the street, on a beach, in a car, abandoned building, bus or train station, or in a park)**

LA31995-6

 

2\. Think about the place you live. Do you have problems with any of the following? \* (96778-6)

**Pests such as bugs, ants, or mice**

LA31996-4

Nuruzzaman, N., Broadwin, M., Kourouma, K., & Olson, D. P. (2015). Making the Social Determinants of Health a Routine Part of Medical Care. Journal of Healthcare for the Poor and Underserved, 26(2), 321-327

 

**Mold**

LA28580-1

 

 

**Lead paint or pipes**

LA31997-2

 

 

**Lack of heat**

LA31998-0

 

 

**Oven or stove not working**

LA31999-8

 

 

**Smoke detectors missing or not working**

LA32000-4

 

 

**Water leaks**

LA32001-2

 

 

None of the above

LA9-3

 

3\. In the past 12 months has the electric, gas, oil, or water company threatened to shut off services in your home? (96779-4)

**Yes**

LA33-6

Cook, J. T., Frank, D. A., Casey, P. H., Rose-Jacobs, R., Black, M. M., Chilton, M., . . . Cutts, D. B. (2008). A Brief Indicator of Household Energy Security: Associations with Food Security, Child Health, and Child Development in US Infants and Toddlers. Pediatrics, 122(4), 867-875. doi:10.1542/peds.2008-0286

 

No

LA32-8

 

 

**Already shut off**

LA32002-0

 

4\. Within the past 12 months, you worried that your food would run out before you got money to buy more. (88122-7)

**Often true**

LA28397-0

Hager, E. R., Quigg, A. M., Black, M. M., Coleman, S. M., Heeren, T., Rose-Jacobs, R., Cook, J. T., Ettinger de Cuba, S. E., Casey, P. H., Chilton, M., Cutts, D. B., Meyers A. F., Frank, D. A. (2010). Development and Validity of a 2-Item Screen to Identify Families at Risk for Food Insecurity. Pediatrics, 126(1), 26-32. doi:10.1542/peds.2009-3146.

 

**Sometimes true**

LA6729-3

 

 

Never true

LA28398-8

 

5\. Within the past 12 months, the food you bought just didn't last and you didn't have money to get more. (88123-5)

**Often true**

LA28397-0

Hager, E. R., Quigg, A. M., Black, M. M., Coleman, S. M., Heeren, T., Rose-Jacobs, R., Cook, J. T., Ettinger de Cuba, S. E., Casey, P. H., Chilton, M., Cutts, D. B., Meyers A. F., Frank, D. A. (2010). Development and Validity of a 2-Item Screen to Identify Families at Risk for Food Insecurity. Pediatrics, 126(1), 26-32. doi:10.1542/peds.2009-3146.

 

**Sometimes true**

LA6729-3

 

 

Never true

LA28398-8

 

6\. In the past 12 months, has lack of reliable transportation kept you from medical appointments, meetings, work or from getting things needed for daily living? (93030-5)

**Yes**

LA33-6

National Association of Community Health Centers and Partners, National Association of Community Health Centers, Association of Asian Pacific Community Health Organizations, Association OPC, Institute for Alternative Futures. (2017). PRAPARE. http://www.nachc.org/research-and-data/prapare

 

No

LA32-8

 

7\. Do you want help finding or keeping work or a job? (96780-2)

**Yes, help finding work**

LA31981-6

Identifying and Recommending Screening Questions for the Accountable Health Communities Model (2016, July) Technical Expert Panel discussion conducted at the U.S. Department of Health and Human Services, Centers for Medicare & Medicaid Services, Baltimore, MD.

 

**Yes, help keeping work**

LA31982-4

 

 

I do not need or want help

LA31983-2

 

8\. Do you want help with school or training? For example, starting or completing job training or getting a high school diploma, GED or equivalent. (96782-8)

**Yes**

LA33-6

Identifying and Recommending Screening Questions for the Accountable Health Communities Model (2016, July) Technical Expert Panel discussion conducted at the U.S. Department of Health and Human Services, Centers for Medicare & Medicaid Services, Baltimore, MD.

 

No

LA32-8

 

9\. How often does anyone, including family and friends, physically hurt you? (95618-5)

Never (1)

LA6270-8

Sherin, K. M., Sinacore, J. M., Li, X. Q., Zitter, R. E., & Shakil, A. (1998). HITS: a Short Domestic Violence Screening Tool for Use in a Family Practice Setting. Family Medicine, 30(7), 508-512

 

Rarely (2)

LA10066-1

 

 

Sometimes (3)

LA10082-8

 

 

Fairly often (4)

LA16644-9

 

 

Frequently (5)

LA6482-9

 

10\. How often does anyone, including family and friends, insult or talk down to you? (95617-7)

Never (1)

LA6270-8

Sherin, K. M., Sinacore, J. M., Li, X. Q., Zitter, R. E., & Shakil, A. (1998). HITS: a Short Domestic Violence Screening Tool for Use in a Family Practice Setting. Family Medicine, 30(7), 508-512

 

Rarely (2)

LA10066-1

 

 

Sometimes (3)

LA10082-8

 

 

Fairly often (4)

LA16644-9

 

 

Frequently (5)

LA6482-9

 

11\. How often does anyone, including family and friends, threaten you with harm? (95616-9)

Never (1)

LA6270-8

Sherin, K. M., Sinacore, J. M., Li, X. Q., Zitter, R. E., & Shakil, A. (1998). HITS: a Short Domestic Violence Screening Tool for Use in a Family Practice Setting. Family Medicine, 30(7), 508-512

 

Rarely (2)

LA10066-1

 

 

Sometimes (3)

LA10082-8

 

 

Fairly often (4)

LA16644-9

 

 

Frequently (5)

LA6482-9

 

12\. How often does anyone, including family and friends, scream or curse at you? (95615-1)

Never (1)

LA6270-8

Sherin, K. M., Sinacore, J. M., Li, X. Q., Zitter, R. E., & Shakil, A. (1998). HITS: a Short Domestic Violence Screening Tool for Use in a Family Practice Setting. Family Medicine, 30(7), 508-512Sherin, K. M., Sinacore, J. M., Li, X. Q., Zitter, R. E., & Shakil, A. (1998). HITS: a Short Domestic Violence Screening Tool for Use in a Family Practice Setting. Family Medicine, 30(7), 508-512

 

Rarely (2)

LA10066-1

 

 

Sometimes (3)

LA10082-8

 

 

Fairly often (4)

LA16644-9

 

 

Frequently (5)

LA6482-9

 

Total Safety Score (95614-4)

Sum question #9-12 above. **Score of 11 or more may indicate that a person may not be safe.**

 

Sherin, K. M., Sinacore, J. M., Li, X. Q., Zitter, R. E., & Shakil, A. (1998). HITS: a Short Domestic Violence Screening Tool for Use in a Family Practice Setting. Family Medicine, 30(7), 508-512

#### Ensuring a Screen is complete[](#ensuring-a-screen-is-complete)

If a screening is asked through direct questioning, screening questions can be skipped at the discretion of the Member or screener. Please note however that all safety questions (#9-12) must be answered to produce an accurate safety score. When a question is skipped during direct questioning, the following logic will ensure a screening is complete:

1.  If a Member does decide to skip any questions, please create an Observation Screening Response with Observation.value: null and use Observation.dataAbsentReason: [Asked but Declined](https://hl7.org/fhir/R4/valueset-data-absent-reason.html).
2.  If the person screening the member decides not to ask a question, please create an Observation Screening Response with Observation.value: null and use Observation.dataAbsentReason: [Not Asked](https://hl7.org/fhir/R4/valueset-data-absent-reason.html) and include a text explanation as to why (e.g., Question was not appropriate to ask at time of screening.)"

#### Eligibility Assessment[](#eligibility-assessment)

ResourceType

UseCase

**Bundle\***

Gathers a collection of resources into a single instance with containing context.5

**Patient\***

Includes key demographic information needed for Member identification.

**Sexual Orientation Observation\***

US Core resource for sexual orientation.

**Encounter\***

Important for the modality of the episode of care and to identify the encounter it happened in.

**Organization\***

Important to identify where the assessment is from.

**Practitioner\***

Important to identify who performed the assessment.

**Condition\***

Recorded confirmed patient HRSN condition if applicable. We would expect to see both a SNOMED and ICD-10 code. _Only required if a patient does have a condition from an unmet need and is going to potentially be referred for services._

**ObservationAssessment**

This is not a required ResourceType. However including this ResourceType may provide more details about the eligibility assessment.

**Eligibility Assessment Approval Questionnaire and QuestionnaireResponse\*** (SHINNYApprovalQuestionnaire)

There will be multiple questionnaires and questionnaire responses within an eligibility assessment to ensure data components of the minimum viable dataset have a resource. This resource(s) captures if moving ahead to an eligibility assessment has been approved or denied. This may be sent without an Eligibility Assessment if the Member denied services.

**Eligibility Assessment Outreach Questionnaire and QuestionnaireResponse\*** (SHINNYOutreachQuestionnaire)

This resource captures when a Member was contacted for an eligibility assessment. This may be sent without an Eligibility Assessment if the Member was never reached.

**Eligibility Assessment Administration Questionnaire and QuestionnaireResponse\*** (SHINNYAdministrativeQuestionnaire)

This resource(s) captures enhanced population, service duplication and medical necessity checks performed by an assessor.

**Eligibility Assessment Member Questionnaire and QuestionnaireResponse\*** (SHINNYServiceDuplicationQuestionnaire)

This resource(s) captures additional service duplication and service planning questions asked to a Member.

**Goal**

Represents a “goal established to address an unmet social risk.6” Not required until year 3.

_\*Required_

#### Referral (Navigation)[](#referral-navigation)

Please see the referral workflow to understand how these resource types will dynamically be exchanged in a data flow. Please note we would not expect a task or procedure if a Member is being navigated to state or federal services.

ResourceType

UseCase

**Bundle\***

Gathers a collection of resources into a single instance with containing context.7

**Patient\***

Includes key demographic information needed for Member identification.

**Sexual Orientation Observation\***

US Core resource for sexual orientation.

**Encounter\***

Important for the modality of the episode of care and to identify the encounter it happened in. Expected encounter from referrer and HRSN service provider.

**Organization\***

Important to identify where the Service Request is from and then when a task is sent, where this is from. If just a Service Request is sent out, one organization resource is expected. If a Task is returned, two organization resources are expected.

**Practitioner\***

Important to identify the individual referring and completing services. If just a Service Request is sent out, one practitioner resource is expected. If a Task is returned, two practitioner resources are expected.

**ServiceRequest\***

Documents initial referral.

**Task**

Documents response from organization performing service to fulfill an unmet need.

**Procedure**

Documents a provision of service to fill unmet need.

**Referral Approval Questionnaire and QuestionnaireResponse\***

Member has approved initial referral to either service navigation or HRSN services. This may be sent without a referral if the Member denies a referral.

**Referral Outreach Date Questionnaire and QuestionnaireResponse\***

When the Member was contacted for a referral. This may be sent without a referral if the Member was never reached.

**HRSN Outreach Date Questionnaire and QuestionnaireResponse\***

When the Member was contacted for a referral. This may be sent without a referral if the Member was never reached.

_\*Required_

#### HRSN Bundle Expectations for Encounter Scenarios[](#hrsn-bundle-expectations-for-encounter-scenarios)

The purpose of this section is to set expectations about the types of resources expected for 1115 Waiver episodes of care.

##### Scenario 1[](#scenario-1)

Screener conducts Screening in their electronic health record but then Eligibility Assessment and Referral is performed in the SCN IT Platform (by provider or SCN Lead Entities).

**Encounter 1**

ResourceType

**Bundle\***

**Consent\***

**Patient\***

**Sexual Orientation Observation\***

**Organization\***

**Encounter\***

**Screening Observation\***

**Screening Questionnaire**

**Screening Questionnaire Response**

**Encounter 2**

ResourceType

**Bundle\***

**Patient\***

**Sexual Orientation Observation\***

**Organization\***

**Encounter\***

**Practitioner\***

**Condition\***

**Observation Assessment**

**Eligibility Approval Questionnaire\***

**Eligibility Assessment Approval QuestionnaireResponse\***

**Eligibility Assessment Outreach Questionnaire\***

**Eligibility Assessment Outreach QuestionnaireResponse\***

**Eligibility Assessment Administration Questionnaire\***

**Eligibility Assessment Administration QuestionnaireResponse\***

**Eligibility Assessment Member Questionnaire\***

**Eligibility Assessment Member QuestionnaireResponse\***

**Goal**

**Referral Approval Questionnaire\***

**Referral Approval QuestionnaireResponse\***

**Referral Outreach Date Questionnaire\***

**Referral Outreach Date QuestionnaireResponse\***

**ServiceRequest\***

Then the following information will follow to show referral is being completed by the HRSN Service Provider:

ResourceType

**Bundle\***

**Patient\***

**Sexual Orientation Observation\***

**Organization\***

**Encounter\***

**Practitioner\***

**ServiceRequest\***

**Task\***

**Procedure\***

**HRSN Outreach Date Questionnaire\***

**HRSN Outreach Date QuestionnaireResponse\***

_\*Required_

##### Scenario 2[](#scenario-2)

Screening, Eligibility Assessment and Navigation are performed in one visit.

ResourceType

**Bundle\***

**Consent\***

**Patient\***

**Sexual Orientation Observation\***

**Organization\***

**Encounter\***

**Screening Observation\***

**Screening Questionnaire**

**Screening Questionnaire Response**

**Practitioner\***

**Condition\***

**Observation Assessment**

**Eligibility Approval Questionnaire\***

**Eligibility Assessment Approval QuestionnaireResponse\***

**Eligibility Assessment Outreach Questionnaire\***

**Eligibility Assessment Outreach QuestionnaireResponse\***

**Eligibility Assessment Administration Questionnaire\***

**Eligibility Assessment Administration QuestionnaireResponse\***

**Eligibility Assessment Member Questionnaire\***

**Eligibility Assessment Member QuestionnaireResponse\***

**Goal**

**Referral Approval Questionnaire\***

**Referral Approval QuestionnaireResponse\***

**Referral Outreach Date Questionnaire\***

**Referral Outreach Date QuestionnaireResponse\***

**ServiceRequest\***

Then the following information will follow to show referral is being completed by the HRSN Service Provider:

ResourceType

**Bundle\***

**Patient\***

**Sexual Orientation Observation\***

**Organization\***

**Encounter\***

**Practitioner\***

**ServiceRequest\***

**Task\***

**Procedure\***

**HRSN Outreach Date Questionnaire\***

**HRSN Outreach Date QuestionnaireResponse\***

_\*Required_

### Referral Workflow[](#referral-workflow)

The SHIN-NY would expect the following steps as defined by the resource types expected for a referral:

1.  A Member may be contacted for service navigation if the referral is not being conducted in the same visit as the Screening and/or Eligibility Assessment.
2.  A member approves service navigation or referral to HRSN services.
3.  A ServiceRequest is sent to HRSN service providers or to service navigation and a copy to the SHIN-NY.
4.  The HRSN service provider contacts the Member.
5.  The HRSN service provider accepts the ServiceRequest through a Task.
6.  Then the Task can be updated to show this work is “In-progress”. This is sent to the SHIN-NY.
7.  Finally, when the service is completed, the HRSN service provider marks the Task to be complete, attaches a procedure with a provision of service code, and the SCN Lead Entity marks the ServiceRequest as complete. Finally, a copy of this is sent to the SHIN-NY.

![](ReferralWorkflow.png)

Artifact 3: Referral workflows between SCN IT platform, SHIN-NY and MEdicaid (OHIP).

![](GracityProjectTaskStatuses.png)

Artifact 4: Gravity Project task statuses found \[here\](https://build.fhir.org/ig/HL7/fhir-sdoh-clinicalcare/StructureDefinition-SDOHCC-TaskForReferralManagement.html).

##### Statuses[](#statuses)

There are specific statuses needed to ensure a finished and complete Screening, Eligibility Assessment, and Referral sent to OHIP. This artifact below shows these specific statuses that should be utilized for each HRSN data type.

![](Statuses.png)

Artifact 5: SHIN-NY statuses needed to ensure a complete submission to OHIP.

#### Encounter Type[](#encounter-type)

Encounter Type is an important indicator of modality, particularly related to Screening completion. It is important that this is used to differentiate screening types for NYS to identify the type of Screening sent to the SHIN-NY Data Lake.

UseCase

Code

Display

System

If an individual is completing a screening online or via text message.

23918007

History taking, self-administered, by computer terminal

http://snomed.info/sct

Used for screenings done by a screener, assessment, and referral.

405672008

Direct questioning

http://snomed.info/sct

#### Organization Type[](#organization-type)

Organization types in HL7 FHIR are currently geared to the clinical communities. NYS has come up with the following terminology to differentiate SCN Lead Entities from other HRSN service providers. If you are not a HRSN service provider or SCN Lead Entity, please use another code and display within this system to differentiate yourself.

UseCase

Code

Display

System

SCN Lead Entities

Other

Other

https://hl7.org/fhir/R4/codesystem-organization-type.html

HRSN Service Provider

Cg

Community Group

https://hl7.org/fhir/R4/codesystem-organization-type.html

### Minimum Viable Data Set[](#minimum-viable-data-set)

NYS has developed a minimum viable data set for SCNs to follow. Please find the minimum viable data set [here](https://nyehealth.sharepoint.com/sites/NYHER1115Extranet/Shared%20Documents/Forms/AllItems.aspx) with mappings to FHIR attributes in the IG.

#### Validation Rules[](#validation-rules)

Right now, the minimum viable data set is enforced through warnings. If certain data is not sent from the value set a warning will be sent back to the SCN IT Platform that sent the data.

#### Terminology[](#terminology)

The terminology in this section contains the systems, codes, and displays expected to be utilized for each HRSN data type in the 1115 Waiver. The most up-to-date documents can be found [here](https://nyehealth.sharepoint.com/sites/NYHER1115Extranet/Shared%20Documents/Forms/AllItems.aspx?ovuser=0bbf351d%2D0e12%2D4503%2D9e73%2Dcde433401057%2Ctlichtenberg%40nyehealth%2Eorg&OR=Teams%2DHL&CT=1733502318363&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiI1MC8yNDEwMjAwMTMxNiIsIkhhc0ZlZGVyYXRlZFVzZXIiOnRydWV9). Specifically reference the NYHER Social Care Coding document and the Enhanced Services Screening to Services Code Mapping document. Note this documentation may change over time, but the most up-to-date files can be accessed using the link above.

If you need access to the SharePoint link above, please send a request to rwagers@nyehealth.org.

<script type="text/javascript" src="assets/js/jquery.js"></script><script type="text/javascript" src="assets/js/jquery-ui.min.js"></script><script type="text/javascript" src="assets/js/window-hash.js"></script>

IG © 2024+ [shinny](https://shinny.org/us/ny/hrsn/index.html). Package us.ny.hrsn#1.4.5 based on [FHIR 4.0.1](http://hl7.org/fhir/R4/). Generated 2025-05-12  
Links: [Table of Contents](toc.html) | [QA Report](qa.html)

<script type="text/javascript" src="assets/js/bootstrap.min.js"></script><script type="text/javascript" src="assets/js/respond.min.js"></script><script type="text/javascript" src="assets/js/anchor.min.js"></script><script type="text/javascript" src="assets/js/clipboard.min.js"></script><script type="text/javascript" src="assets/js/clipboard-btn.js"></script><script type="text/javascript" src="assets/js/anchor-hover.js"></script>

## Embedded Content