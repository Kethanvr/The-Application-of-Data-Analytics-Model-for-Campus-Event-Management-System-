# CEMS — Campus Event Management System

<div align="center">

![Django](https://img.shields.io/badge/Django-5.0.1-green?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![MongoDB](https://img.shields.io/badge/Database-MongoDB_Atlas-47A248?style=for-the-badge&logo=mongodb)
![Bootstrap](https://img.shields.io/badge/UI-Bootstrap_4-purple?style=for-the-badge&logo=bootstrap)
![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=for-the-badge&logo=render)

**A full-stack Django web application for managing the complete lifecycle of campus events — from proposal to certificates.**

*Built for CMR Institute of Technology, Bengaluru. Backed by MongoDB Atlas.*

</div>

---

## Live Demo

The app is deployed on **Render** and connected to **MongoDB Atlas**.

> **URL:** *(add your Render URL here after deployment)*

---

## Login Credentials

All accounts below are pre-loaded with full mock data (events, registrations, assessments, feedback).

### Principal (Admin)
| Field | Value |
|---|---|
| Username | `admin` |
| Password | `Admin@123` |
| Access | Final approval of all events, institutional analytics dashboard, view all departments |

### Event Coordinators
| Username | Password | Department |
|---|---|---|
| `coord_cse` | `Coord@123` | Computer Science |
| `coord_ise` | `Coord@123` | Information Science |
| `coord_ece` | `Coord@123` | Electronics & Communication |
| `coord_mech` | `Coord@123` | Mechanical Engineering |

### Heads of Department (HOD)
| Username | Password | Department |
|---|---|---|
| `hod_cse` | `Hod@123` | Computer Science |
| `hod_ise` | `Hod@123` | Information Science |
| `hod_ece` | `Hod@123` | Electronics & Communication |

### Students
| Username | Password | USN | Department |
|---|---|---|---|
| `student_01` | `Student@123` | 1CR21CS001 | CSE |
| `student_02` | `Student@123` | 1CR21IS002 | ISE |
| `student_03` | `Student@123` | 1CR21EC003 | ECE |
| `student_04` | `Student@123` | 1CR21CS004 | CSE |
| `student_05` | `Student@123` | 1CR21ME005 | Mechanical |
| `testuser1`  | `student123`  | —          | CSE |

> **Register a new account** at `/register/` — choose any role and department.

---

## How to Use the Website

### As a Student
1. Log in with any `student_*` account
2. Go to **Browse Events** — see all approved events open for registration
3. Click **Register Now** on an event you want to join
4. After the event, go to **Assessments** and take the quiz
5. Once scored, go to **My Certificates** and download your PDF certificate
6. Check **Online Events** for events with Zoom/Meet links
7. Download **Study Materials** from registered events

### As an Event Coordinator
1. Log in with `coord_cse` / `Coord@123`
2. Click **Create Event** — fill in event details, budget, and mode
3. Your event enters the approval pipeline:
   - Status: `PENDING` → `HOD_APPROVED` → `PRINCIPAL_APPROVED`
4. Once approved, the event is visible to students for registration
5. Go to **Assessments** → **Create Assessment** to add a quiz for your event
6. View **Submissions** to see student scores and grade answers
7. Go to **Event Scheduler** to add sessions for online events
8. Upload **Study Materials** for participants

### As a HOD
1. Log in with `hod_cse` / `Hod@123`
2. See **Pending Review** — events from your department awaiting your decision
3. Click **View Details** to read the full proposal, budget, and coordinator info
4. Click **Approve** to forward to Principal, or **Reject** with a reason
5. View **Approved** and **Rejected** tabs for history
6. Go to **Analytics** for department-level statistics and charts

### As Principal
1. Log in with `admin` / `Admin@123`
2. See **Pending Review** — HOD-approved events waiting for final clearance
3. **Final Approve** or **Reject** with a reason
4. Go to **Analytics** for institution-wide dashboard:
   - Total events by department (bar chart)
   - Event status breakdown (doughnut chart)
   - Assessment performance metrics
   - AI-powered approval insights

---

## What's Pre-loaded (Mock Data)

After running `seed_data`, the database contains:

| Collection | Count | Description |
|---|---|---|
| Users | 19 | 1 Principal, 4 Coordinators, 3 HODs, 8 Students + extras |
| Events | 11 | 6 Approved, 2 HOD-Approved, 2 Pending, 1 Rejected |
| Registrations | 39 | Students registered across approved events |
| Assessments | 6 | One per approved event with 5 MCQ questions each |
| Submissions | 29 | Students who completed assessments (scores 40–100%) |
| Feedback | 24 | Star ratings + comments from students |
| Schedules | 28 | 7 sessions per event for the first 4 events |
| Materials | 18 | 3 study materials per approved event |

---

## Quick Start — Run Locally

### Prerequisites
- Python 3.10+
- MongoDB Atlas account (free tier works) **or** local MongoDB 6+ on `localhost:27017`
- Git

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/cems.git
cd cems
```

### 2. Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env — set your MONGODB_URI and SECRET_KEY
```

`.env` format:
```env
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/eventwebsite?retryWrites=true&w=majority
SECRET_KEY=your-secret-key-here
```

### 5. Run migrations and seed users
```bash
python manage.py migrate --run-syncdb
python manage.py seed_users          # Creates admin + testuser1
python manage.py seed_data           # Loads full demo dataset (recommended)
```

### 6. Start the server
```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## Re-seed / Reset Data

```bash
# Clear all event data and re-seed from scratch
python manage.py seed_data --clear

# Only seed users (Principal + Student)
python manage.py seed_users
```

---

## Event Approval Workflow

```
Event Coordinator creates event
         ↓  status: PENDING
   HOD reviews (department filter)
     → Approve  → status: HOD_APPROVED
     → Reject   → status: HOD_REJECTED
         ↓  HOD_APPROVED
  Principal reviews (all departments)
     → Approve  → status: PRINCIPAL_APPROVED  ← students can now register
     → Reject   → status: PRINCIPAL_REJECTED
```

---

## Deploy to Render

1. Push code to GitHub
2. Go to [Render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Set build & start:
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn dems.wsgi:application`
5. Add environment variables:

| Variable | Value |
|---|---|
| `MONGODB_URI` | Your MongoDB Atlas connection string (database: `eventwebsite`) |
| `SECRET_KEY` | A long random string |
| `RENDER` | `true` |

The `build.sh` script automatically:
- Installs Python dependencies
- Collects static files (WhiteNoise)
- Creates Django session tables
- Runs `seed_users` to create demo accounts

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Django 5.0.1 |
| Database | MongoDB Atlas (MongoEngine ODM) |
| Frontend | Bootstrap 4, Chart.js 4, Font Awesome 6 |
| Auth | Custom MongoEngine backend + session middleware |
| Analytics | scikit-learn, pandas, numpy |
| PDF / Certificates | Pillow, qrcode |
| Web Server | Gunicorn |
| Static Files | WhiteNoise |
| Sessions | django-session-timeout (SQLite) |

---

## Project Structure

```
cems/
├── dems/
│   ├── settings.py          # MongoDB connection, middleware, auth
│   ├── urls.py              # Root URL config
│   └── wsgi.py
├── users/
│   ├── models.py            # CustomUser (MongoEngine Document)
│   ├── backends.py          # MongoDB auth backend
│   ├── middleware.py        # MongoAuthMiddleware (session → user)
│   ├── views.py             # login, register, dashboard, profile
│   └── management/
│       └── commands/
│           └── seed_users.py
├── events/
│   ├── models.py            # Event, Assessment, Registration… (11 models)
│   ├── views.py             # All event views (~1200 lines)
│   ├── urls.py              # 30+ URL patterns
│   ├── dashboard_api.py     # JSON API endpoints for dashboard
│   ├── ai_assessment.py     # AI-powered assessment generation
│   ├── utils.py             # Certificate generation (PIL + QR)
│   └── management/
│       └── commands/
│           └── seed_data.py # Full demo data seeder
├── users/templates/users/   # base.html, login, register, dashboard, profile
├── events/templates/events/ # 20+ HTML templates
├── build.sh                 # Render deployment script
├── requirements.txt
├── .env.example
└── manage.py
```

---

<div align="center">
Made with ❤️ by CMRIT Students &nbsp;|&nbsp; Django + MongoDB Atlas + Render
</div>
