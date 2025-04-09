import os
import shutil
import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection


class Command(BaseCommand):
    help = 'Backup SQLite database file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dir',
            default='backups',
            help='Directory to store backups (relative to project root)',
        )

    def handle(self, *args, **options):
        if not settings.DATABASES['default']['ENGINE'].endswith('sqlite3'):
            self.stderr.write('This command only works with SQLite databases')
            return
            
        db_path = settings.DATABASES['default']['NAME']
        if not os.path.exists(db_path):
            self.stderr.write(f'Database file not found: {db_path}')
            return
            
        # Ensure database is consistent by checkpointing any WAL files
        with connection.cursor() as cursor:
            cursor.execute('PRAGMA wal_checkpoint(FULL);')

        # Create backup directory if it doesn't exist
        backup_dir = Path(settings.BASE_DIR) / options['dir']
        backup_dir.mkdir(exist_ok=True)
        
        # Generate timestamped backup filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f"db_backup_{timestamp}.sqlite3"
        
        # Copy the database file
        try:
            shutil.copy2(db_path, backup_path)
            self.stdout.write(self.style.SUCCESS(
                f'Database backed up successfully to {backup_path}'
            ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f'Backup failed: {str(e)}'
            ))