# Campus Event Management System (CEMS)

CEMS is a Django application for coordinating campus events through a role-based workflow. The project includes event proposals and approvals, student registration, assessments, certificates, schedules, study materials, and analytics views.

This is a student project and local demo. The repository includes sample-data seeding commands; do not use demo accounts or sample data as production identities or records. No shared login credentials are published here.

## Run locally

Requirements: Python 3.10 or newer and a database configuration supported by the project.

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env

Configure the local values required by the project in `.env`, then initialize and start the app:

    python manage.py migrate --run-syncdb
    python manage.py seed_users
    python manage.py seed_data
    python manage.py runserver

The development server is available at `http://127.0.0.1:8000/`. Use seeded accounts only in a local development environment and set fresh credentials before any deployment.

## Project structure

- `events/` contains event workflows and related views.
- `users/` contains account and role-related code.
- `dems/` contains Django project configuration.

Do not commit `.env` files or local database files. Review all demo data before sharing or deploying this project.
