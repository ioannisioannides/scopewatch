#!/usr/bin/env python
"""
Complete Database and Migration Reset

This script performs a full reset of the migration history in the database
without modifying any migration files. It:

1. Creates a backup of your current database
2. Identifies all apps with migrations
3. Deletes all migration records from django_migrations
4. Marks all existing migrations as applied with --fake

This is a simpler approach that avoids dealing with complex migration dependencies.

Usage:
    python reset_all_migrations.py
"""

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
    """Create a backup of the database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/db_backup_{timestamp}.json"

    # Ensure backup directory exists
    Path("backups").mkdir(exist_ok=True)

    print(f"Creating database backup to {backup_file}...")
    try:
        subprocess.run(
            [
                "python",
                "manage.py",
                "dumpdata",
                "--exclude",
                "contenttypes",
                "--exclude",
                "auth.Permission",
                "--exclude",
                "sessions",
                "--indent",
                "2",
                "-o",
                backup_file,
            ],
            check=True,
        )
        print("✅ Database backup completed")
        return backup_file
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Warning: Failed to create backup: {e}")
        choice = input("Continue anyway? [y/N]: ").lower()
        if choice != "y":
            print("Operation cancelled")
            sys.exit(1)
        return None


def identify_all_apps():
    """Find all Django apps with migrations"""
    from django.apps import apps

    all_apps = []
    for app_config in apps.get_app_configs():
        migrations_dir = Path(app_config.path) / "migrations"
        if migrations_dir.exists():
            all_apps.append(app_config.label)

    # Sort to ensure consistent order
    all_apps.sort()
    return all_apps


def reset_migration_history():
    """Delete all migration records from the database"""
    connection = connections["default"]

    print("Clearing migration history...")
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM django_migrations;")

    print("✅ Migration history cleared")
    return True


def fake_apply_migrations():
    """Apply migrations with --fake for all apps"""
    print("\nApplying migrations with --fake flag...")

    # Apply in the correct order: first Django's built-in apps
    core_apps = ["contenttypes", "auth", "admin", "sessions"]
    for app in core_apps:
        try:
            print(f"Fake migrating {app}...")
            subprocess.run(["python", "manage.py", "migrate", app, "--fake"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Failed to fake migrate {app}: {e}")

    # Then apply apps in proper dependency order
    try:
        # First cert bodies and organizations which are base apps
        subprocess.run(
            ["python", "manage.py", "migrate", "certification_bodies", "--fake"], check=True
        )
        subprocess.run(["python", "manage.py", "migrate", "organizations", "--fake"], check=True)

        # Then audits which depends on them
        subprocess.run(["python", "manage.py", "migrate", "audits", "--fake"], check=True)

        # Then all remaining apps
        subprocess.run(["python", "manage.py", "migrate", "--fake"], check=True)

        print("✅ All migrations marked as applied")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error applying migrations: {e}")
        return False


def verify_migrations():
    """Run migrations normally to verify everything is consistent"""
    print("\nVerifying migration consistency...")

    try:
        subprocess.run(["python", "manage.py", "migrate", "--check"], check=True)
        print("✅ Migration history is now consistent!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Migrations still inconsistent")
        return False


def main():
    print("=" * 60)
    print("🔄 Complete Database Migration Reset")
    print("=" * 60)
    print("This script will reset the entire migration history in your database.")
    print("It will NOT delete or modify any data except the migration history.")

    # Confirm before proceeding
    choice = input("\nDo you want to continue? [y/N]: ").lower()
    if choice != "y":
        print("Operation cancelled")
        return 1

    # Create database backup
    backup_file = create_backup()

    # Get all apps with migrations
    apps = identify_all_apps()
    print(f"Found {len(apps)} apps with migrations: {', '.join(apps)}")

    # Reset migration history
    if not reset_migration_history():
        print("❌ Failed to reset migration history")
        return 1

    # Fake apply migrations
    if not fake_apply_migrations():
        print("\n❌ Failed to fake apply migrations")
        print(f"You can restore your database from backup: {backup_file}")
        return 1

    # Verify migrations
    if not verify_migrations():
        print("\n⚠️ Migration verification failed")
        print("Your migrations are marked as applied, but there might still be inconsistencies.")
        print("If you encounter problems, you may need to run specific app migrations with --fake.")
        print(f"You can restore your database from backup: {backup_file}")
        return 1

    print("\n✅ Migration reset completed successfully!")
    print("Your database can now be managed with standard Django commands.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
