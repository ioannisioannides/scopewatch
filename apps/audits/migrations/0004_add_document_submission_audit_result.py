from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('consultants', '0001_initial'),
        ('certification_bodies', '0003_certbody_contact_email_certbody_is_active_auditor_and_more'),
        ('audits', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('document_type', models.CharField(choices=[('policy', 'Policy Document'), ('procedure', 'Procedure'), ('record', 'Record'), ('evidence', 'Compliance Evidence'), ('report', 'Report'), ('other', 'Other')], max_length=20)),
                ('submitted_at', models.DateTimeField(default=timezone.now)),
                ('status', models.CharField(choices=[('submitted', 'Submitted'), ('under_review', 'Under Review'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('needs_revision', 'Needs Revision')], default='submitted', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('file', models.FileField(upload_to='audit_documents/')),
                ('audit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='audits.audit')),
                ('consultant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prepared_documents', to='consultants.consultant')),
                ('submitted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submitted_documents', to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='AuditResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('decision', models.CharField(choices=[('approve', 'Approve Certification'), ('conditional', 'Conditional Approval'), ('reject', 'Reject Certification'), ('followup', 'Followup Audit Required')], max_length=20)),
                ('decision_date', models.DateField(default=timezone.now)),
                ('notes', models.TextField(blank=True)),
                ('nonconformances_closed', models.BooleanField(default=False)),
                ('recommendation', models.CharField(blank=True, choices=[('issue', 'Issue Certificate'), ('withhold', 'Withhold Certificate'), ('withdraw', 'Withdraw Certificate'), ('followup', 'Followup Required')], max_length=20)),
                ('audit', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='audits.audit')),
                ('decided_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='audit_decisions', to='certification_bodies.certbodyuser')),
            ],
        ),
    ]