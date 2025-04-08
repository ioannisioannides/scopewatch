from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0007_add_certification_scope_and_audit_link'),
        ('audits', '0004_add_document_submission_audit_result'),
        ('consultants', '0003_consultancyfirm_created_at_consultant_firm_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsultantDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('document_type', models.CharField(choices=[('policy', 'Policy Document'), ('procedure', 'Procedure'), ('work_instruction', 'Work Instruction'), ('form', 'Form Template'), ('record', 'Record'), ('manual', 'Manual'), ('other', 'Other')], max_length=20)),
                ('standard', models.CharField(help_text='The standard this document is prepared for', max_length=255)),
                ('created_at', models.DateTimeField(default=timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('review', 'Under Review'), ('approved', 'Approved by Organization'), ('submitted', 'Submitted to Audit'), ('rejected', 'Rejected'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('file', models.FileField(upload_to='consultant_documents/')),
                ('notes', models.TextField(blank=True)),
                ('consultant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='consultants.consultant')),
                ('engagement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='consultants.consultantengagement')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consultant_documents', to='organizations.organization')),
                ('submitted_to_audit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='submitted_consultant_documents', to='audits.audit')),
            ],
        ),
    ]