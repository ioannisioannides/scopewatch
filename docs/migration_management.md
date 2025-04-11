# Django Migration Management Guide

## Overview

This guide documents our approach to managing Django migrations, particularly focusing on how we've resolved the recurring migration dependency issues in our CI/CD pipeline.

## The Problem

We've been experiencing inconsistent migration history errors, specifically:
- Migration dependencies being applied in the wrong order
- Missing migrations referenced by other migrations
- CI/CD pipeline failing due to migration errors

## The Solution: Squashed Migrations

We've implemented a comprehensive solution using Django's migration squashing feature, which:
1. Combines multiple migrations into a single file
2. Creates a cleaner migration history
3. Eliminates complex dependencies between apps
4. Makes our CI/CD pipeline more reliable

## Tools We've Created

### 1. `reset_migrations.py`

A script that handles the entire migration reset process:
- Creates database backups
- Generates squashed migrations for each app
- Resets the migration history in the database
- Cleans up old migration files

**Usage:**
```bash
# Full reset with all steps
python reset_migrations.py

# Dry run to see what would happen without making changes
python reset_migrations.py --dry-run

# Run specific steps only
python reset_migrations.py --backup --squash
```

### 2. `update_local_dev_db.py`

A script for developers to update their local environments after migration changes:
- Creates a backup of your current database
- Handles applying the new migrations correctly
- Provides clear instructions for common issues

**Usage:**
```bash
# Update your local DB while preserving data
python update_local_dev_db.py

# Reset your local DB completely (use with caution!)
python update_local_dev_db.py --reset
```

## Workflow for Developers

### When You Pull Changes with Squashed Migrations

1. Run the update script:
   ```bash
   python update_local_dev_db.py
   ```

2. If you encounter issues, try resetting your database:
   ```bash
   python update_local_dev_db.py --reset
   ```

### When Creating New Migrations

1. Always create migrations from the main branch
2. Test your migrations locally before pushing
3. Make sure to run full test suite with migrations

## Migration Guidelines

1. **Keep dependencies simple**: Avoid creating complex cross-app dependencies
2. **Be explicit about dependencies**: Always specify app dependencies in `models.py`
3. **Test migrations**: Ensure migrations can be applied to a fresh database
4. **Commit migrations separately**: Make separate commits for code changes and migration changes

## Troubleshooting Common Issues

### InconsistentMigrationHistory Error

If you see an error like:
```
django.db.migrations.exceptions.InconsistentMigrationHistory: Migration app_name.XXXX is applied before its dependency...
```

Try:
```bash
# Apply specific migration with --fake
python manage.py migrate app_name migration_name --fake

# Then run normal migrations
python manage.py migrate
```

### Failed Migration Operation

If a specific migration fails:
1. Check the error message carefully
2. Try running with `--fake` flag for that specific migration
3. If needed, restore from your backup

## Squashing Migrations Periodically

We should consider squashing migrations approximately every 6 months or when:
- We have more than 20 migrations in a single app
- Migration run time gets too long
- We encounter recurring migration issues

## Further Reading

- [Django Migrations Documentation](https://docs.djangoproject.com/en/stable/topics/migrations/)
- [Django Squashing Migrations](https://docs.djangoproject.com/en/stable/topics/migrations/#squashing-migrations)
- [Django Migration Operations](https://docs.djangoproject.com/en/stable/ref/migration-operations/)
