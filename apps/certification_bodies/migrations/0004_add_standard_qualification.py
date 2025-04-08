from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("certification_bodies", "0001_initial"),
    ]

    operations = [
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
                    models.FileField(
                        blank=True, null=True, upload_to="auditor_qualifications/"
                    ),
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
