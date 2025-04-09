from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        # Replace the non-existent migration with ones that definitely exist
        ("organizations", "0001_initial"),
        ("organizations", "0002_certification"),
        ("organizations", "0003_remove_certification_is_active_and_more"),
        ("organizations", "0004_organization_is_active"),
    ]

    operations = [
        migrations.CreateModel(
            name="SearchLog",
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
                ("search_term", models.CharField(max_length=255)),
                ("search_date", models.DateTimeField(default=timezone.now)),
                ("results_count", models.IntegerField(default=0)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="CertificationVerification",
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
                ("verification_date", models.DateTimeField(default=timezone.now)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                (
                    "certificate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="verification_records",
                        to="organizations.certification",
                    ),
                ),
            ],
        ),
    ]
