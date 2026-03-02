#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install required packages
python -m pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run Django migrations (only for sessions/contenttypes SQLite tables)
python manage.py migrate --run-syncdb

# Seed default demo users into MongoDB (skips if they already exist)
python manage.py seed_users
