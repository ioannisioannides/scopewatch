#!/bin/bash
# Deployment script for Scopewatch
# This script runs database migrations and collects static files

set -e  # Exit immediately if a command exits with a non-zero status

# Ensure we're in the project directory (where manage.py is located)
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
  echo "Activating virtual environment..."
  if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
  elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
  fi
fi

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
if command -v gunicorn &> /dev/null; then
  exec gunicorn scopewatch.wsgi:application --bind 0.0.0.0:8000
else
  echo "Error: gunicorn not found. Please install it with: pip install gunicorn"
  exit 1
fi