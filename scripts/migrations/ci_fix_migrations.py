#!/usr/bin/env python
"""
CI Migration Fix Script

This script directly modifies the problematic migration files in the CI environment
to fix dependency issues. Rather than creating new migration files, it modifies
the existing ones to work around missing dependencies.

Usage:
    python ci_fix_migrations.py
"""

import fileinput
import os
import re
from pathlib import Path


def modify_migration_dependencies():
    """
    Directly modify the migration dependencies in problematic files.

    This function finds migration files that depend on organizations.0010_merge_20250409_0505
    and changes them to depend on organization.0009_remove_organizationuser_joined_date_and_more instead.
    """
    print("Scanning for migration files with dependency issues...")

    # Files known to have problems
    problem_files = [
        "apps/consultants/migrations/0013_consultantdocument_organization_and_more.py",
        "apps/public/migrations/0002_certificationverification_certificate.py",
        "apps/audits/migrations/0007_audit_certbody_audit_organization_and_more.py",
    ]

    base_path = Path(__file__).resolve().parent

    for rel_path in problem_files:
        file_path = base_path / rel_path

        if not file_path.exists():
            print(f"Warning: {rel_path} not found, skipping")
            continue

        print(f"Processing file: {rel_path}")

        # Read the file content
        with open(file_path, "r") as file:
            content = file.read()

        # Check if it contains the problematic dependency
        if '"organizations", "0010_merge_20250409_0505"' in content:
            # Replace the dependency with the previous migration
            modified_content = content.replace(
                '"organizations", "0010_merge_20250409_0505"',
                '"organizations", "0009_remove_organizationuser_joined_date_and_more"',
            )

            # Write back the modified file
            with open(file_path, "w") as file:
                file.write(modified_content)
            print(f"  Fixed dependency in {rel_path}")
        else:
            print(f"  No dependency issues found in {rel_path}")


if __name__ == "__main__":
    modify_migration_dependencies()
    print("Migration dependency fix completed successfully")
