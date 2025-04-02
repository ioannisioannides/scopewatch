#!/usr/bin/env python3
"""
manage.py

Django's command-line utility for administrative tasks in the Scopewatch project.

This script is used to manage the application, including running the server,
applying migrations, and other administrative tasks.
"""

import os
import sys

from django.core.management import \
    execute_from_command_line  # Moved to the top-level


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scopewatch.settings')
    try:
        execute_from_command_line(sys.argv)
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure it's installed and "
            "available on your PYTHONPATH environment variable. Did you "
            "forget to activate a virtual environment?"
        ) from exc


if __name__ == '__main__':
    main()
