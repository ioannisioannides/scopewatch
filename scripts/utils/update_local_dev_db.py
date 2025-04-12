#!/usr/bin/env python
"""
Local Development Database Update Script

This script helps developers update their local development environment
after the migration reset. It:

1. Creates a backup of your current database
2. Handles applying the new migrations correctly
3. Provides clear instructions for common issues

Run this script when:
- You've just pulled changes that include squashed migrations
- You're encountering migration errors in your local environment

Usage:
    python update_local_dev_db.py [--reset]

Options:
    --reset    Completely reset your database (use with caution!)
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import django
from django.db import connections

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scopewatch.settings")
django.setup()


def create_backup():
    """Create a backup of the local database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/local_db_backup_{timestamp}.json"

    # Ensure backups directory exists
    Path("backups").mkdir(exist_ok=True)

    print(f"\n1️⃣ Creating a backup of your database to {backup_file}...")
    try:
        result = subprocess.run(
            [
                "python",
                "manage.py",
                "dumpdata",
                "--exclude",
                "contenttypes",
                "--exclude",
                "auth.Permission",
                "--indent",
                "2",
                "-o",
                backup_file,
            ],
            check=True,
            text=True,
        )
        if result.returncode != 0:
            raise ValueError("Backup command failed")
        print("✅ Database backup created successfully")
        return backup_file
    except (ValueError, OSError, subprocess.CalledProcessError) as e:
        print(f"⚠️ Warning: Failed to create database backup: {e}")
        choice = input("Continue anyway? [y/N]: ").lower()
        if choice != "y":
            print("Operation cancelled")
            sys.exit(1)
        return None


def reset_database():
    """Reset the database completely"""
    print("\n2️⃣ Resetting your database completely...")

    try:
        # Drop all tables
        connection = connections["default"]
        with connection.cursor() as cursor:
            if connection.vendor == "sqlite":
                # For SQLite, we'll recreate the database file
                db_path = connection.settings_dict["NAME"]
                if os.path.exists(db_path):
                    os.remove(db_path)
                open(db_path, "w", encoding="utf-8").close()  # Create an empty file
            else:
                # For other databases, drop all tables
                tables = connection.introspection.table_names()
                for table in tables:
                    print(f"Dropping table: {table}")
                    cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")

        print("✅ Database reset successfully")
    except Exception as e:
        print(f"⚠️ Error resetting database: {str(e)}")
        print("Continuing with migrations anyway...")


def fake_migrations():
    """Apply migrations with --fake flag"""
    print("\n3️⃣ Applying migrations with --fake flag...")

    try:
        subprocess.run(
            ["python", "manage.py", "migrate", "--fake-initial", "contenttypes"],
            check=True,
            text=True,
        )
        subprocess.run(
            ["python", "manage.py", "migrate", "--fake-initial", "auth"], check=True, text=True
        )
        subprocess.run(
            ["python", "manage.py", "migrate", "--fake-initial", "admin"], check=True, text=True
        )
        subprocess.run(["python", "manage.py", "migrate", "--fake-initial"], check=True, text=True)

        print("✅ Migrations applied with --fake flag")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error applying migrations: {e}")
        print("\nTry running the migrations manually with:")
        print("  python manage.py migrate --fake-initial")


def apply_real_migrations():
    """Apply migrations normally"""
    print("\n4️⃣ Applying migrations normally...")

    try:
        subprocess.run(["python", "manage.py", "migrate"], check=True)
        print("✅ Migrations applied successfully")
    except subprocess.CalledProcessError:
        print("⚠️ Error applying migrations normally")
        print("\nYou may need to fix specific migrations. Try:")
        print("1. python manage.py migrate app_name 0001 --fake")
        print("2. python manage.py migrate")


def restore_backup(backup_file):
    """Restore data from the backup"""
    print(f"\n5️⃣ Restoring data from backup {backup_file}...")

    try:
        result = subprocess.run(
            ["python", "manage.py", "loaddata", backup_file], check=True, text=True
        )
        if result.returncode != 0:
            raise ValueError("Restore command failed")
        print("✅ Data restored successfully")
    except (ValueError, OSError, subprocess.CalledProcessError) as e:
        print(f"⚠️ Error restoring data: {e}")
        print("\nYou may need to load the backup manually:")
        print(f"  python manage.py loaddata {backup_file}")


def main():
    parser = argparse.ArgumentParser(description="Update local development database")
    parser.add_argument("--reset", action="store_true", help="Reset the database completely")
    args = parser.parse_args()

    print("=" * 60)
    print("🔄 Local Development Database Update")
    print("=" * 60)
    print("This script will help you update your local database after migration changes.")

    # Create a backup first
    backup_file = create_backup()

    if args.reset:
        # Reset the database completely
        reset_database()

    # Apply migrations with --fake flag
    fake_migrations()

    # Apply migrations normally
    apply_real_migrations()

    # Ask if user wants to restore the backup
    if backup_file and os.path.exists(backup_file):
        choice = input("\nDo you want to restore data from the backup? [y/N]: ").lower()
        if choice == "y":
            restore_backup(backup_file)

    print("\n✅ Database update completed!")
    print("\nIf you encounter any issues:")
    print("1. Try running 'python manage.py migrate --fake-initial'")
    print("2. Check for any specific migration errors in the output")
    print("3. If needed, restore your database from the backup:")
    if backup_file:
        print(f"   python manage.py loaddata {backup_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
