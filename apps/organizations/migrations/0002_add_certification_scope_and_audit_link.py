from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('audits', '0001_initial'),
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='certification',
            name='scope',
            field=models.TextField(blank=True, help_text='The scope of certification - what activities, processes, or sites are covered.'),
        ),
        migrations.AddField(
            model_name='certification',
            name='audit',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resulting_certification', to='audits.audit'),
        ),
    ]