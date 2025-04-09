import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection


class Command(BaseCommand):
    help = 'Optimize the SQLite database for better performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--vacuum',
            action='store_true',
            help='Run VACUUM to rebuild the database file',
        )
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Run ANALYZE to update statistics used by the query planner',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all optimization operations',
        )

    def handle(self, *args, **options):
        if not settings.DATABASES['default']['ENGINE'].endswith('sqlite3'):
            raise CommandError('This command only works with SQLite databases')

        db_path = settings.DATABASES['default']['NAME']
        
        if not os.path.exists(db_path):
            raise CommandError(f'Database file not found: {db_path}')

        self.stdout.write(f'Optimizing SQLite database: {db_path}')
        
        # Always run PRAGMA optimize
        with connection.cursor() as cursor:
            self.stdout.write('Running PRAGMA optimize...')
            cursor.execute('PRAGMA optimize;')
            
            # Run PRAGMA wal_checkpoint to ensure WAL file is processed
            self.stdout.write('Running PRAGMA wal_checkpoint...')
            cursor.execute('PRAGMA wal_checkpoint(FULL);')
            
            # Set the cache size
            self.stdout.write('Setting cache size...')
            cursor.execute('PRAGMA cache_size = -65536;')  # 64MB cache
            
            # Enable memory-mapped I/O
            self.stdout.write('Enabling memory-mapped I/O...')
            cursor.execute('PRAGMA mmap_size = 268435456;')  # 256MB

        if options['vacuum'] or options['all']:
            self.stdout.write('Running VACUUM...')
            with connection.cursor() as cursor:
                cursor.execute('VACUUM;')
        
        if options['analyze'] or options['all']:
            self.stdout.write('Running ANALYZE...')
            with connection.cursor() as cursor:
                cursor.execute('ANALYZE;')
        
        self.stdout.write(self.style.SUCCESS('Database optimization complete.'))