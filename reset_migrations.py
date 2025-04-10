#!/usr/bin/env python
"""
Django Migration Reset Script

This script provides a complete solution to the recurring migration issues by:
1. Identifying all your Django apps
2. Generating squashed migrations for each app
3. Clearing the migration history in the database
4. Marking the squashed migrations as applied
5. Cleaning up old migration files

Run this script with:
python reset_migrations.py [--dry-run] [--backup] [--squash] [--reset-db] [--clean]

Options:
  --dry-run    Show what would be done without making changes
  --backup     Create a database backup before proceeding
  --squash     Generate squashed migrations
  --reset-db   Reset the migration history in the database
  --clean      Remove old migration files
"""

import os
import sys
import argparse
import shutil
import subprocess
import django
from datetime import datetime
from pathlib import Path
from django.db import connections
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scopewatch.settings')
django.setup()

def create_backup(dry_run=False):
    """Create a backup of the database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/db_backup_{timestamp}.json"
    
    # Ensure backup directory exists
    Path("backups").mkdir(exist_ok=True)
    
    print(f"Creating database backup to {backup_file}...")
    if not dry_run:
        subprocess.run([
            "python", "manage.py", "dumpdata",
            "--exclude", "contenttypes",
            "--exclude", "auth.Permission",
            "--exclude", "sessions",
            "--indent", "2",
            "-o", backup_file
        ])
    print("✅ Database backup completed")
    return backup_file

def identify_django_apps():
    """Find all Django apps in the project with their correct labels"""
    # Get app configs from settings
    app_configs = []
    for app in settings.INSTALLED_APPS:
        # Skip Django built-in apps
        if not app.startswith('django.') and not app.startswith('rest_framework'):
            if '.' in app:
                # For apps with dotted paths, take the last part
                app_name = app.split('.')[-1]
                app_configs.append((app_name, app))
            else:
                # For apps without dotted paths
                app_configs.append((app, app))
    
    # Remove duplicates and sort
    unique_apps = {}
    for name, label in app_configs:
        # Prefer the shorter label if both exist
        if name in unique_apps:
            if len(label) < len(unique_apps[name]):
                unique_apps[name] = label
        else:
            unique_apps[name] = label
    
    return unique_apps

def get_latest_migration(app):
    """Get the latest migration number for an app"""
    base_path = Path(__file__).resolve().parent
    
    # Check both potential locations for migrations
    paths_to_check = [
        base_path / app / "migrations",
        base_path / "apps" / app / "migrations"
    ]
    
    for migrations_path in paths_to_check:
        if not migrations_path.exists():
            continue
            
        # Find all migration files
        migrations = []
        for file in migrations_path.glob("*.py"):
            if file.name != "__init__.py" and not file.name.startswith("__"):
                # Extract migration number
                if file.name.startswith("0"):
                    number = file.name.split("_")[0]
                    if number.isdigit():
                        migrations.append((int(number), file.name))
        
        if migrations:
            # Sort by number and get the latest
            migrations.sort(key=lambda x: x[0], reverse=True)
            return migrations[0][1].split(".")[0]  # Remove .py extension
    
    return None

def get_migrations_path(app):
    """Get the path to migrations for an app"""
    base_path = Path(__file__).resolve().parent
    
    # Check both potential locations
    app_migrations = base_path / app / "migrations"
    apps_migrations = base_path / "apps" / app / "migrations"
    
    if app_migrations.exists() and app_migrations.is_dir():
        return app_migrations
    elif apps_migrations.exists() and apps_migrations.is_dir():
        return apps_migrations
    
    return None

def squash_migrations(app_dict, dry_run=False):
    """Generate squashed migrations for all apps"""
    print("\nSquashing migrations for all apps...")
    squashed_migrations = {}
    
    for app_name, app_label in app_dict.items():
        latest = get_latest_migration(app_name)
        if latest:
            # Determine squash range
            squash_name = f"0001_squashed_{latest}"
            print(f"Squashing {app_name} migrations (0001 to {latest})...")
            
            if not dry_run:
                try:
                    # Use the correct app label for squashmigrations command
                    subprocess.run([
                        "python", "manage.py", "squashmigrations",
                        app_label, "0001", latest,
                        "--no-optimize"  # Keep all operations for maximum compatibility
                    ], check=True)
                    squashed_migrations[app_name] = squash_name
                except subprocess.CalledProcessError as e:
                    print(f"⚠️  Error squashing migrations for {app_name}: {e}")
            else:
                squashed_migrations[app_name] = squash_name
                
    print("✅ Squashing migrations complete")
    return squashed_migrations

def reset_db_migration_history(squashed_migrations, app_dict, dry_run=False):
    """Clear migration history and mark squashed migrations as applied"""
    print("\nResetting migration history in database...")
    if not dry_run:
        # Get the default database connection
        connection = connections['default']
        with connection.cursor() as cursor:
            # Delete all migration records
            cursor.execute("DELETE FROM django_migrations;")
            
            # Mark squashed migrations as applied
            for app_name, squash_name in squashed_migrations.items():
                app_label = app_dict.get(app_name, app_name)
                cursor.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, NOW());",
                    [app_label, squash_name]
                )
        print("✅ Migration history has been reset in database")
    else:
        print("Would delete all records from django_migrations table")
        for app_name, squash_name in squashed_migrations.items():
            app_label = app_dict.get(app_name, app_name)
            print(f"Would mark {app_label}.{squash_name} as applied")

def clean_old_migrations(app_dict, squashed_migrations, dry_run=False):
    """Remove old migration files, keeping only squashed ones"""
    print("\nCleaning up old migration files...")
    
    for app_name, squash_name in squashed_migrations.items():
        migrations_path = get_migrations_path(app_name)
        if not migrations_path:
            continue
            
        print(f"Cleaning {app_name} migrations...")
        
        # Find migration files to delete
        for file in migrations_path.glob("*.py"):
            if file.name == "__init__.py" or file.name == f"{squash_name}.py":
                continue
                
            if not dry_run:
                try:
                    file.unlink()
                    print(f"Deleted: {file}")
                except Exception as e:
                    print(f"Error deleting {file}: {e}")
            else:
                print(f"Would delete: {file}")
    
    print("✅ Old migration files cleaned up")

def fix_inconsistent_history():
    """Fix inconsistent migration history by applying fake migrations"""
    print("\nApplying fake migrations to fix inconsistent history...")
    
    # First, apply contenttypes and auth migrations with --fake
    subprocess.run(["python", "manage.py", "migrate", "contenttypes", "--fake"], check=True)
    subprocess.run(["python", "manage.py", "migrate", "auth", "--fake"], check=True)
    
    # Specifically handle the problematic migrations
    subprocess.run(["python", "manage.py", "migrate", "certification_bodies", "0003_certbodyuser_contact_phone", "--fake"], check=True)
    subprocess.run(["python", "manage.py", "migrate", "audits", "0006_change_audit_status_choices", "--fake"], check=True)
    
    # Then fake the rest
    subprocess.run(["python", "manage.py", "migrate", "--fake"], check=True)
    
    print("✅ Applied fake migrations")

def create_empty_fixed_migration(app, name, dependencies, dry_run=False):
    """Create an empty migration with specific dependencies"""
    print(f"Creating empty migration {app}.{name}...")
    
    if not dry_run:
        # Create migration using makemigrations --empty
        subprocess.run([
            "python", "manage.py", "makemigrations",
            "--empty",
            "--name", name,
            app
        ], check=True)
        
        # Now find the created migration file
        migrations_path = get_migrations_path(app)
        if not migrations_path:
            print(f"⚠️  Could not find migrations path for {app}")
            return False
            
        # Find the most recent migration
        latest_migration = None
        highest_number = -1
        for file in migrations_path.glob("*.py"):
            if file.name != "__init__.py" and not file.name.startswith("__"):
                # Extract migration number
                if file.name.startswith("0"):
                    number = file.name.split("_")[0]
                    if number.isdigit() and int(number) > highest_number:
                        highest_number = int(number)
                        latest_migration = file
                        
        if latest_migration:
            # Modify the dependencies
            with open(latest_migration, 'r') as f:
                content = f.read()
                
            # Replace dependencies
            deps_str = ',\n        '.join([f'("{app}", "{dep}")' for app, dep in dependencies])
            new_content = content.replace(
                "dependencies = [",
                f"dependencies = [\n        {deps_str}"
            )
            
            with open(latest_migration, 'w') as f:
                f.write(new_content)
                
            print(f"Created and modified {latest_migration}")
            return True
    else:
        print(f"Would create empty migration for {app}")
        
    return False

def main():
    parser = argparse.ArgumentParser(description="Reset and squash Django migrations")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--backup", action="store_true", help="Create a database backup before proceeding")
    parser.add_argument("--squash", action="store_true", help="Generate squashed migrations")
    parser.add_argument("--reset-db", action="store_true", help="Reset the migration history in the database")
    parser.add_argument("--clean", action="store_true", help="Remove old migration files")
    parser.add_argument("--fix", action="store_true", help="Fix inconsistent migration history")
    
    args = parser.parse_args()
    dry_run = args.dry_run
    
    # If no specific actions specified, do everything
    if not (args.backup or args.squash or args.reset_db or args.clean or args.fix):
        args.backup = True
        args.fix = True  # Default to fix mode instead of full squash
    
    if dry_run:
        print("⚠️  DRY RUN - No changes will be made")
    
    # Identify all Django apps
    app_dict = identify_django_apps()
    print(f"Found {len(app_dict)} Django apps: {', '.join(app_dict.keys())}")
    
    # Create database backup
    if args.backup:
        backup_file = create_backup(dry_run)
    
    # Fix inconsistent migration history
    if args.fix:
        if not dry_run:
            # Create specific missing migrations
            create_empty_fixed_migration(
                "certification_bodies",
                "0003_certbodyuser_contact_phone", 
                [("certification_bodies", "0002_alter_certbody_options")],
                dry_run
            )
            
            # Apply fake migrations
            try:
                fix_inconsistent_history()
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Error applying migrations: {e}")
                print("\nTrying alternate approach...")
                # Try specific problem migrations
                subprocess.run(["python", "manage.py", "migrate", "certification_bodies", "--fake"], check=True)
                subprocess.run(["python", "manage.py", "migrate", "audits", "--fake"], check=True)
        else:
            print("Would fix inconsistent migration history")
    
    # Squash migrations
    squashed_migrations = {}
    if args.squash:
        squashed_migrations = squash_migrations(app_dict, dry_run)
    
    # Reset database migration history
    if args.reset_db and squashed_migrations:
        reset_db_migration_history(squashed_migrations, app_dict, dry_run)
    
    # Clean up old migration files
    if args.clean and squashed_migrations:
        clean_old_migrations(app_dict, squashed_migrations, dry_run)
    
    print("\n✅ Migration reset completed successfully!")
    print("\nNext steps:")
    print("1. Run 'python manage.py migrate' to validate the migrations")
    print("2. Update your CI workflow to use this script")
    print("3. Inform all developers to reset their local databases")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())