# Generated manually to reset migrations
"""
Reset migrations for consultants app.

This migration replaces all previous migrations with a clean state
that matches the current model definitions.
"""

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Reset migration for consultants app."""

    # This replaces all previous migrations
    replaces = [
        ("consultants", "0001_initial"),
        ("consultants", "0002_remove_consultancyfirm_created_at_and_more"),
        ("consultants", "0003_consultancyfirm_created_at_consultant_firm_and_more"),
        ("consultants", "0004_add_consultant_document"),
        ("consultants", "0005_merge_20250408_0423"),
        ("consultants", "0006_remove_consultancyfirm_is_active_and_more"),
        ("consultants", "0007_consultancyfirm_is_active"),
        ("consultants", "0008_fix_migration_dependency"),
        ("consultants", "0009_ensure_dependencies_compatibility"),
        ("consultants", "0010_fix_dependencies_for_consultant_document"),
        ("consultants", "0011_merge_20250409_0419"),
    ]

    # Define initial state (no dependencies on previous migrations)
    initial = True

    # Dependencies on other apps that this migration requires
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("organizations", "0001_initial"),
        ("audits", "0001_initial"),
    ]

    operations = [
        # Create ConsultancyFirm model
        migrations.CreateModel(
            name="ConsultancyFirm",
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
                ("address", models.CharField(blank=True, max_length=255)),
                ("contact_email", models.EmailField(blank=True, max_length=254, null=True)),
                ("website", models.URLField(blank=True)),
                ("specialties", models.CharField(blank=True, max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        # Create Consultant model
        migrations.CreateModel(
            name="Consultant",
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
                ("bio", models.TextField(blank=True)),
                ("specialties", models.CharField(blank=True, max_length=255)),
                ("specialty", models.CharField(blank=True, max_length=255)),
                ("standards", models.CharField(blank=True, max_length=255)),
                ("experience_years", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("is_independent", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "firm",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="consultants",
                        to="consultants.consultancyfirm",
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
        # Create ConsultantEngagement model
        migrations.CreateModel(
            name="ConsultantEngagement",
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
                ("start_date", models.DateField(default=django.utils.timezone.now)),
                ("end_date", models.DateField(blank=True, null=True)),
                ("standards", models.CharField(default="ISO 9001", max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("completed", "Completed"),
                            ("on_hold", "On Hold"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="active",
                        max_length=20,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                (
                    "consultant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="engagements",
                        to="consultants.consultant",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consultant_engagements",
                        to="organizations.organization",
                    ),
                ),
            ],
        ),
        # Create ConsultantDocument model
        migrations.CreateModel(
            name="ConsultantDocument",
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
                ("title", models.CharField(max_length=255)),
                (
                    "document_type",
                    models.CharField(
                        choices=[
                            ("policy", "Policy Document"),
                            ("procedure", "Procedure"),
                            ("work_instruction", "Work Instruction"),
                            ("form", "Form Template"),
                            ("record", "Record"),
                            ("manual", "Manual"),
                            ("other", "Other"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "standard",
                    models.CharField(
                        help_text="The standard this document is prepared for", max_length=255
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("review", "Under Review"),
                            ("approved", "Approved by Organization"),
                            ("submitted", "Submitted to Audit"),
                            ("rejected", "Rejected"),
                            ("archived", "Archived"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("file", models.FileField(upload_to="consultant_documents/")),
                ("notes", models.TextField(blank=True)),
                (
                    "consultant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="consultants.consultant",
                    ),
                ),
                (
                    "engagement",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="consultants.consultantengagement",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consultant_documents",
                        to="organizations.organization",
                    ),
                ),
                (
                    "submitted_to_audit",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="submitted_consultant_documents",
                        to="audits.audit",
                    ),
                ),
            ],
        ),
    ]