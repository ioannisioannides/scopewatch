import pytest
from django.core.management import call_command
from django.db import connection
from django.db.migrations.exceptions import InconsistentMigrationHistory

def test_migration_order():
    with pytest.raises(InconsistentMigrationHistory):
        call_command('migrate', 'audits', '0007_audit_certbody_audit_organization_and_more', database='default')