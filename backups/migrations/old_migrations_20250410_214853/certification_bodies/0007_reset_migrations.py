# Generated manually to reset migrations
"""
Reset migrations for certification_bodies app.

This migration replaces all previous migrations with a clean state
that matches the current model definitions.
"""

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Reset migration for certification_bodies app."""

    # This replaces all previous migrations
    replaces = [
        ("certification_bodies", "0001_initial"),
        ("certification_bodies", "0002_remove_certbody_contact_email_and_more"),
        ("certification_bodies", "0003_certbody_contact_email_certbody_is_active_auditor_and_more"),
        ("certification_bodies", "0004_add_standard_qualification"),
        ("certification_bodies", "0005_merge_20250408_0423"),
        ("certification_bodies", "0006_remove_certbodyuser_joined_date_auditor_bio_and_more"),
    ]

    # Define initial state (no dependencies on previous migrations)
    initial = True

    # Dependencies on other apps that this migration requires
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Create CertBody model
        migrations.CreateModel(
            name="CertBody",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("accreditation_id", models.CharField(max_length=100)),
                ("address", models.CharField(blank=True, max_length=255)),
                ("logo", models.ImageField(blank=True, null=True, upload_to="certbody_logos/")),
                ("contact_email", models.EmailField(blank=True, max_length=254, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        # Create CertBodyUser model
        migrations.CreateModel(
            name="CertBodyUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("admin", "Administrator"),
                            ("manager", "Manager"),
                            ("certifier", "Certification Manager"),
                            ("staff", "Staff Member"),
                        ],
                        max_length=20,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "cert_body",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="users",
                        to="certification_bodies.certbody",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        # Create Auditor model
        migrations.CreateModel(
            name="Auditor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("specialties", models.CharField(blank=True, max_length=255)),
                ("bio", models.TextField(blank=True)),
                ("employee_id", models.CharField(blank=True, max_length=50)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "cert_bodies",
                    models.ManyToManyField(
                        related_name="auditors",
                        to="certification_bodies.certbody",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        # Create StandardQualification model
        migrations.CreateModel(
            name="StandardQualification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("standard", models.CharField(max_length=255)),
                ("qualification_date", models.DateField()),
                ("expiry_date", models.DateField(blank=True, null=True)),
                (
                    "evidence_document",
                    models.FileField(blank=True, null=True, upload_to="auditor_qualifications/"),
                ),
                ("notes", models.TextField(blank=True)),
                (
                    "auditor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="qualifications",
                        to="certification_bodies.auditor",
                    ),
                ),
                (
                    "cert_body",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="verified_qualifications",
                        to="certification_bodies.certbody",
                    ),
                ),
            ],
            options={
                "unique_together": {("auditor", "standard", "cert_body")},
            },
        ),
    ]
