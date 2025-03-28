# Scopewatch Architecture

This document provides a high-level view of the Scopewatch system architecture and data model. It focuses on the primary entities and relationships for managing compliance frameworks, audits, and certifications.

---

## Overview

Scopewatch aims to bring together:
- **Organizations** seeking certifications.
- **Certification Bodies** conducting audits and issuing certificates.
- **Auditors** who gather evidence and generate findings.
- **Consultants** (future feature) assisting organizations with compliance.
- **Public portal** for verification of certificates.

At a high level, the system is built on:

- **Django** (Python) for the backend logic and data models.
- **PostgreSQL** as the main relational database (though dev setups might use SQLite).
- (Optional) **Docker** for containerizing the application and its services.
- **TailwindCSS** (potentially) for front-end styling.
- (Planned) **Stripe** integration for billing or subscription models.

---

## Entity-Relationship Diagram (ERD)

Below is a **Mermaid.js** diagram showcasing **key entities** and their relationships. This covers Organizations, Certification Bodies, Audits, Nonconformances, Certificates, and (optionally) Consultants.

```mermaid
erDiagram
    %% ---------------------
    %% USER & ROLE MANAGEMENT
    %% ---------------------

    USER {
        int id PK
        string username
        string email
        string password
        string first_name
        string last_name
        boolean is_active
        date date_joined        
    }

    ROLE {
        int id PK
        string name "SuperUser, OrgAdmin, OrgUser, CBAdmin, Auditor, Consultant"
        string description
    }

    USER_ROLE {
        int id PK
        int user_id FK
        int role_id FK "multi-tenant, multiple privileges"
    }

    %% ---------------------
    %% ORGANIZATIONS
    %% ---------------------

    ORGANIZATION {
        int id PK
        string name
        string address
        string contact_email
        string contact_phone
        boolean is_active
        date created_at
    }

    ORGANIZATION_USER {
        int id PK
        int user_id FK
        int organization_id FK
        string org_role "Admin, Editor, Viewer"
        date joined_date
        boolean is_active
    }

    %% ---------------------
    %% CERTIFICATION BODIES
    %% ---------------------

    CERTBODY {
        int id PK
        string name
        string accreditation_id "Some reference to official accreditation"
        string address
        string contact_email
        date created_at
        boolean is_active
    }

    CERTBODY_USER {
        int id PK
        int user_id FK
        int certbody_id FK
        string cb_role "Admin, Auditor, Secretary, Accountant"
        boolean is_active
        date joined_date
    }

    %% ---------------------
    %% CONSULTANTS & CONSULTANCY FIRMS
    %% ---------------------

    CONSULTANCY_FIRM {
        int id PK
        string name
        string address
        string contact_email
        boolean is_active
        date created_at
    }

    CONSULTANCY_FIRM_USER {
        int id PK
        int user_id FK
        int consultancy_firm_id FK
        string role_in_firm "Lead Consultant, Junior Consultant"
        boolean is_active
        date joined_date
    }

    %% A direct Consultant might be an individual not in a firm,
    %% but we can unify them via the same tables or have them in a "firm" of size 1.
    %% Alternatively, you might choose a simpler approach, but this is an example.

    %% ---------------------
    %% RELATION: CONSULTANT <--> ORGANIZATION
    %% (Consultants can help Orgs with compliance)
    %% ---------------------

    CONSULTANT_ENGAGEMENT {
        int id PK
        int consultant_user_id FK  "references USER who has a Consultant role, possibly from a consultancy_firm"
        int organization_id FK
        date start_date
        date end_date
        boolean is_active
        string engagement_details  "Scope of consulting, contract details"
    }

    %% ---------------------
    %% AUDITS
    %% ---------------------

    AUDIT {
        int id PK
        int organization_id FK
        int certbody_id FK
        string audit_type "Pre-assessment, Stage1, Stage2, etc."
        date start_date
        date end_date
        string status "Scheduled, In Progress, Completed, Closed"
        text notes
        date created_at
        date updated_at
    }

    %% Relationship that assigns Auditors (who are under CB) to an Audit
    AUDIT_ASSIGNMENT {
        int id PK
        int audit_id FK
        int certbody_user_id FK "references a user from the CERTBODY, e.g. Auditor"
        date assigned_date
        date unassigned_date
        boolean is_active
    }

    %% ---------------------
    %% STANDARDS & CHECKLISTS
    %% ---------------------

    STANDARD {
        int id PK
        string name "e.g. ISO 9001:2015"
        string version
        text description
        boolean is_active
        date created_at
    }

    CHECKLIST {
        int id PK
        int standard_id FK
        string question
        string guidance
        boolean is_active
    }

    AUDIT_CHECKLIST_RESPONSE {
        int id PK
        int audit_id FK
        int checklist_id FK
        string response "Compliant, Non-compliant, Not Applicable"
        text notes
        date created_at
    }

    %% ---------------------
    %% NON-CONFORMANCES
    %% ---------------------

    NONCONFORMANCE {
        int id PK
        int audit_id FK
        string severity "Major, Minor, Opportunity for Improvement"
        text description
        date date_raised
        date date_closed
        boolean requires_evidence
    }

    NONCONFORMANCE_EVIDENCE {
        int id PK
        int nonconformance_id FK
        string file_path
        text remarks
        date uploaded_at
        int uploaded_by_user_id FK
    }

    %% ---------------------
    %% CERTIFICATIONS & PUBLIC VIEW
    %% ---------------------

    CERTIFICATE {
        int id PK
        int organization_id FK
        int certbody_id FK
        int standard_id FK
        string certificate_number
        date issue_date
        date expiry_date
        boolean is_locked
        date created_at
    }

    CERTIFICATE_UNLOCK_REQUEST {
        int id PK
        int certificate_id FK
        int user_id FK "user requesting to see certificate"
        string reason
        date request_date
        boolean is_approved
        date approval_date
        date unlock_start_date
        date unlock_end_date
    }

    %% ---------------------
    %% RELATIONSHIPS
    %% ---------------------

    %% USER - ROLE
    USER ||--|{ USER_ROLE : "has many roles"

    %% ORGANIZATION - USER (Membership)
    ORGANIZATION ||--|{ ORGANIZATION_USER : "has members"
    USER ||--|{ ORGANIZATION_USER : "belongs to multiple orgs"

    %% CERTBODY - USER (Membership)
    CERTBODY ||--|{ CERTBODY_USER : "has staff"
    USER ||--|{ CERTBODY_USER : "can be staff of multiple CBs"

    %% CONSULTANCY_FIRM - USER
    CONSULTANCY_FIRM ||--|{ CONSULTANCY_FIRM_USER : "has consultants"
    USER ||--|{ CONSULTANCY_FIRM_USER : "can belong to multiple firms (rare but possible)"

    %% CONSULTANT ENGAGEMENT - ORG
    CONSULTANCY_FIRM_USER }|--|{ CONSULTANT_ENGAGEMENT : "performs consulting"
    ORGANIZATION }|--|{ CONSULTANT_ENGAGEMENT : "receives consulting"

    %% AUDIT references ORG & CB
    ORGANIZATION ||--|{ AUDIT : "requests audits"
    CERTBODY ||--|{ AUDIT : "performs audits"

    %% AUDIT_ASSIGNMENT references AUDIT & CB staff (Auditors)
    AUDIT ||--|{ AUDIT_ASSIGNMENT : "audit assigned to auditors"
    CERTBODY_USER ||--|{ AUDIT_ASSIGNMENT : "auditor assigned to many audits"

    %% STANDARDS
    CERTBODY ||..|{ STANDARD : "defines or references many standards"

    %% CHECKLIST
    STANDARD ||--|{ CHECKLIST : "includes many questions"

    %% AUDIT_CHECKLIST_RESPONSE
    AUDIT ||--|{ AUDIT_CHECKLIST_RESPONSE : "has many checklist responses"
    CHECKLIST ||--|{ AUDIT_CHECKLIST_RESPONSE : "is responded to in many audits"

    %% NONCONFORMANCE
    AUDIT ||--|{ NONCONFORMANCE : "might generate NCs"

    %% Evidence
    NONCONFORMANCE ||--|{ NONCONFORMANCE_EVIDENCE : "has evidence"
    USER ||--|{ NONCONFORMANCE_EVIDENCE : "uploads evidence"

    %% CERTIFICATE
    ORGANIZATION ||--|{ CERTIFICATE : "receives certificates"
    CERTBODY ||--|{ CERTIFICATE : "issues certificates"
    STANDARD ||--|{ CERTIFICATE : "certificate references a standard"

    %% Unlock requests
    CERTIFICATE ||--|{ CERTIFICATE_UNLOCK_REQUEST : "can receive multiple unlock requests"
    USER ||--|{ CERTIFICATE_UNLOCK_REQUEST : "makes requests"
