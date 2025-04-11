#!/bin/bash
# Development launcher script for Scopewatch
# This script sets up the development environment and starts the server

# Ensure we're in the project directory
cd "$(dirname "$0")"

# Create .env file from .env.development if it doesn't exist
if [ ! -f ".env" ] && [ -f ".env.development" ]; then
  echo "Creating .env file from .env.development..."
  cp .env.development .env
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
  echo "Activating virtual environment..."
  if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
  elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
  fi
fi

# Run migrations if needed
python manage.py migrate

# Start development server
python manage.py runserver
