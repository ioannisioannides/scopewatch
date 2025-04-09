#!/bin/bash
# Deployment script for Scopewatch
# This script runs database migrations and collects static files

set -e  # Exit immediately if a command exits with a non-zero status

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create or update superuser from environment variables
echo "Checking for superuser credentials in environment variables..."
python manage.py create_or_update_superuser

# Start gunicorn
echo "Starting Gunicorn server..."
exec gunicorn scopewatch.wsgi:application --bind 0.0.0.0:8000