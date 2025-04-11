import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("audits", "0001_initial"),
        (
            "organizations",
            "0002_certification",
        ),  # Updated to depend on the migration that creates the Certification model
    ]

    operations = [
        migrations.AddField(
            model_name="certification",
            name="scope",
            field=models.TextField(
                blank=True,
                help_text="The scope of certification - what activities, processes, or sites are covered.",
            ),
        ),
        migrations.AddField(
            model_name="certification",
            name="audit",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="resulting_certification",
                to="audits.audit",
            ),
        ),
    ]
