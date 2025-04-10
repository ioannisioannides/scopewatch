#!/usr/bin/env python
"""
SQLite database optimization script
Run as: python optimize_sqlite.py
"""
import os
import sys
import sqlite3
import django

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scopewatch.settings")
django.setup()

from django.conf import settings
from pathlib import Path

def optimize_sqlite():
    """Optimize SQLite database"""
    if not settings.DATABASES['default']['ENGINE'].endswith('sqlite3'):
        print("This script only works with SQLite databases")
        return False
        
    db_path = settings.DATABASES['default']['NAME']
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return False

    print(f"Optimizing SQLite database: {db_path}")
    
    try:
        # Connect directly to SQLite without using Django's connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Perform optimizations
        print("Running PRAGMA optimize...")
        cursor.execute('PRAGMA optimize;')
        
        print("Running PRAGMA wal_checkpoint...")
        cursor.execute('PRAGMA wal_checkpoint(FULL);')
        
        # Removed setting cache_size as it's not compatible with Python 3.13
        # print("Setting cache size...")
        # cursor.execute('PRAGMA cache_size = -65536;')  # 64MB cache
        
        print("Enabling memory-mapped I/O...")
        cursor.execute('PRAGMA mmap_size = 268435456;')  # 256MB
        
        print("Running VACUUM...")
        cursor.execute('VACUUM;')
        
        print("Running ANALYZE...")
        cursor.execute('ANALYZE;')
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("Database optimization complete.")
        return True
    except Exception as e:
        print(f"Error optimizing database: {e}")
        return False

def backup_sqlite():
    """Backup SQLite database"""
    if not settings.DATABASES['default']['ENGINE'].endswith('sqlite3'):
        print("This script only works with SQLite databases")
        return False
        
    db_path = settings.DATABASES['default']['NAME']
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return False
    
    try:
        # Connect directly to SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ensure database is consistent
        print("Running PRAGMA wal_checkpoint for consistency...")
        cursor.execute('PRAGMA wal_checkpoint(FULL);')
        cursor.close()
        conn.close()
        
        # Create backup directory
        backup_dir = Path(settings.BASE_DIR) / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        # Generate backup filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f"db_backup_{timestamp}.sqlite3"
        
        # Backup via SQLite's built-in backup API
        print(f"Backing up database to {backup_path}...")
        conn = sqlite3.connect(db_path)
        backup_conn = sqlite3.connect(str(backup_path))
        
        conn.backup(backup_conn)
        
        conn.close()
        backup_conn.close()
        
        print("Database backup complete.")
        return True
    except Exception as e:
        print(f"Error backing up database: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "backup":
        success = backup_sqlite()
    else:
        success = optimize_sqlite()
        
    if not success:
        sys.exit(1)
