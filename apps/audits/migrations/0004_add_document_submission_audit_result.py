from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        # Removed cross-app dependencies
        ("audits", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentSubmission",
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
                            ("record", "Record"),
                            ("evidence", "Compliance Evidence"),
                            ("report", "Report"),
                            ("other", "Other"),
                        ],
                        max_length=20,
                    ),
                ),
                ("submitted_at", models.DateTimeField(default=timezone.now)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("submitted", "Submitted"),
                            ("under_review", "Under Review"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("needs_revision", "Needs Revision"),
                        ],
                        default="submitted",
                        max_length=20,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("file", models.FileField(upload_to="audit_documents/")),
                (
                    "audit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="audits.audit",
                    ),
                ),
                # Removed foreign keys to other apps
            ],
        ),
        migrations.CreateModel(
            name="AuditResult",
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
                    "decision",
                    models.CharField(
                        choices=[
                            ("approve", "Approve Certification"),
                            ("conditional", "Conditional Approval"),
                            ("reject", "Reject Certification"),
                            ("followup", "Followup Audit Required"),
                        ],
                        max_length=20,
                    ),
                ),
                ("decision_date", models.DateField(default=timezone.now)),
                ("notes", models.TextField(blank=True)),
                ("nonconformances_closed", models.BooleanField(default=False)),
                (
                    "recommendation",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("issue", "Issue Certificate"),
                            ("withhold", "Withhold Certificate"),
                            ("withdraw", "Withdraw Certificate"),
                            ("followup", "Followup Required"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "audit",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="result",
                        to="audits.audit",
                    ),
                ),
                # Removed foreign keys to other apps
            ],
        ),
    ]
