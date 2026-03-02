#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install required packages
python -m pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate
