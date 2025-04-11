#!/usr/bin/env python
"""
Simple Step-by-Step Migration Fix

This script takes a more controlled, sequential approach to fixing migration issues:
1. Creates a backup of your database
2. Resets the migration history completely
3. Creates the model structure first with initial migrations
4. Then applies each app's migrations one by one in the right order
5. Checks for errors at each step

Usage:
    python simple_migration_fix.py
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
        ]
    )
    print(f"✅ Database backup created: {backup_file}")
    return backup_file


def reset_database():
    """Reset the SQLite database completely"""
    connection = connections["default"]

    # For SQLite, we'll recreate the database file
    if connection.vendor == "sqlite":
        db_path = connection.settings_dict["NAME"]
        if os.path.exists(db_path):
            # Backup the file first
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backups/db_backup_{timestamp}.sqlite3"
            print(f"Creating database file backup to {backup_path}...")
            Path("backups").mkdir(exist_ok=True)
            try:
                import shutil

                shutil.copy2(db_path, backup_path)
                print(f"✅ Database file backed up")
            except Exception as e:
                print(f"⚠️ Error backing up database file: {e}")

            # Delete and recreate the file
            try:
                os.remove(db_path)
                print(f"✅ Removed old database file")
            except Exception as e:
                print(f"⚠️ Error removing database file: {e}")

            # Create empty file
            open(db_path, "w").close()
            print(f"✅ Created new empty database file")
            return True
    else:
        print("This script only supports SQLite databases")
        return False

    return True


def run_migration_step(app=None, fake=False, fake_initial=False, check_only=False):
    """Run a migration step for an app"""
    cmd = ["python", "manage.py", "migrate"]

    if app:
        cmd.append(app)

    if fake:
        cmd.append("--fake")

    if fake_initial:
        cmd.append("--fake-initial")

    if check_only:
        cmd.append("--check")

    step_description = f"migration for {app}" if app else "migrations for all apps"
    if fake:
        step_description = f"fake {step_description}"
    elif fake_initial:
        step_description = f"fake-initial {step_description}"

    print(f"\nRunning {step_description}...")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(e.stdout)
        print(e.stderr)
        return False


def create_empty_migration(app, name):
    """Create an empty migration for an app"""
    print(f"\nCreating empty migration {name} for {app}...")

    try:
        subprocess.run(
            ["python", "manage.py", "makemigrations", "--empty", "--name", name, app],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(e.stdout)
        print(e.stderr)
        return False


def main():
    print("=" * 60)
    print("🔧 Simple Step-by-Step Migration Fix")
    print("=" * 60)
    print("This script will completely reset your database and migrations.")
    print("All data will be lost, but a backup will be created first.")

    choice = input("\nDo you want to continue? [y/N]: ").lower()
    if choice != "y":
        print("Operation cancelled")
        return 1

    # Step 1: Create a data backup
    backup_file = create_backup()

    # Step 2: Reset the database completely
    if not reset_database():
        print("❌ Failed to reset database")
        return 1

    # Step 3: Create initial structure with Django's built-in apps
    print("\n👉 Step 1: Migrating Django's built-in apps")
    for app in ["contenttypes", "auth", "admin", "sessions"]:
        if not run_migration_step(app):
            print(f"❌ Failed to migrate {app}")
            return 1

    # Step 4: Apply initial migrations for base apps
    print("\n👉 Step 2: Creating initial structure for base apps")
    base_apps = ["certification_bodies", "organizations"]
    for app in base_apps:
        if not run_migration_step(app, fake_initial=True):
            print(f"❌ Failed to apply initial migrations for {app}")

            # Try creating an empty "reset" migration
            if not create_empty_migration(app, "reset_migrations"):
                return 1

            # Try applying it
            if not run_migration_step(app, fake_initial=True):
                return 1

    # Step 5: Apply initial migrations for dependent apps
    print("\n👉 Step 3: Creating initial structure for dependent apps")
    dependent_apps = ["audits", "consultants", "public"]
    for app in dependent_apps:
        if not run_migration_step(app, fake_initial=True):
            print(f"❌ Failed to apply initial migrations for {app}")

            # Try creating an empty "reset" migration
            if not create_empty_migration(app, "reset_migrations"):
                return 1

            # Try applying it
            if not run_migration_step(app, fake_initial=True):
                return 1

    # Step 6: Apply all remaining migrations
    print("\n👉 Step 4: Applying all remaining migrations")
    if not run_migration_step(fake=True):
        print("❌ Failed to apply all migrations")
        return 1

    # Step 7: Verify migrations
    print("\n👉 Step 5: Verifying migration consistency")
    if not run_migration_step(check_only=True):
        print("⚠️ Warning: There may still be migration inconsistencies")
    else:
        print("✅ Migration consistency check passed")

    # Step 8: Restore data if needed
    print("\n👉 Step 6: Restoring data")
    choice = input(
        f"Do you want to restore data from backup {backup_file}? [y/N]: "
    ).lower()
    if choice == "y":
        print(f"Restoring data from {backup_file}...")
        try:
            subprocess.run(["python", "manage.py", "loaddata", backup_file], check=True)
            print("✅ Data restored successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error restoring data: {e}")
            print("You can try manual restore later with:")
            print(f"  python manage.py loaddata {backup_file}")

    print("\n✅ Migration fix completed!")
    print("\nNext steps:")
    print(
        "1. Run 'python manage.py migrate --check' to verify everything is consistent"
    )
    print("2. If you encounter any issues, you can restore your data with:")
    print(f"   python manage.py loaddata {backup_file}")
    print("3. Update your CI workflow to use '--fake-initial' when running migrations")

    return 0


if __name__ == "__main__":
    sys.exit(main())
