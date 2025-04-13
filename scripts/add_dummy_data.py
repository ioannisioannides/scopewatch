from django.utils import timezone
from apps.organizations.models import Organization, Certification
from apps.certification_bodies.models import CertBody, Audit
from apps.consultants.models import ConsultancyFirm, Consultant, ConsultantEngagement
from apps.public.models import SearchLog

def add_dummy_data():
    # Add Certification Body
    cert_body = CertBody.objects.create(
        name="Global Certifiers",
        accreditation_id="GC-12345",
        address="123 Certification Lane",
        contact_email="info@globalcertifiers.com",
        is_active=True
    )

    # Add Organization
    organization = Organization.objects.create(
        name="Tech Innovators",
        address="456 Innovation Drive",
        contact_email="contact@techinnovators.com",
        website="https://techinnovators.com",
        industry="Technology",
        is_active=True
    )

    # Add Certification
    certification = Certification.objects.create(
        organization=organization,
        standard="ISO 9001:2015",
        certificate_number="TI-ISO9001-001",
        issue_date=timezone.now().date(),
        expiry_date=timezone.now().date().replace(year=timezone.now().year + 3),
        scope="Quality Management System",
        audit=None  # Placeholder for now
    )

    # Add Consultant and Consultancy Firm
    consultancy_firm = ConsultancyFirm.objects.create(
        name="Compliance Experts",
        address="789 Compliance Blvd",
        contact_email="support@complianceexperts.com",
        website="https://complianceexperts.com",
        specialties="ISO Standards",
        is_active=True
    )

    consultant = Consultant.objects.create(
        user=None,  # Placeholder for user
        firm=consultancy_firm,
        bio="Experienced consultant in ISO standards.",
        specialties="Quality Management",
        experience_years=10,
        is_active=True,
        is_independent=False
    )

    # Add Consultant Engagement
    engagement = ConsultantEngagement.objects.create(
        consultant=consultant,
        organization=organization,
        start_date=timezone.now().date(),
        standards="ISO 9001:2015",
        status="active"
    )

    # Add Search Log
    SearchLog.objects.create(
        search_term="ISO 9001",
        search_date=timezone.now(),
        results_count=1,
        ip_address="127.0.0.1",
        user_agent="Mozilla/5.0",
        location="Localhost"
    )

    print("Dummy data added successfully.")

if __name__ == "__main__":
    add_dummy_data()