# 🎓 CEMS — Campus Event Management System

<div align="center">

![Django](https://img.shields.io/badge/Django-5.0.1-green?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Supabase](https://img.shields.io/badge/Database-Supabase-3ECF8E?style=for-the-badge&logo=supabase)
![Bootstrap](https://img.shields.io/badge/UI-Bootstrap_4-purple?style=for-the-badge&logo=bootstrap)

**A full-stack Django web application for managing campus events, approvals, assessments, and certificates.**

*Built for CMR Institute of Technology, Bengaluru.*

</div>

---

## 🚀 Quick Start — Run Locally

### Prerequisites
- Python 3.10+
- Git

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/cems.git
cd cems
```

### 2. Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Start the development server
```bash
python manage.py runserver
```

Open your browser and go to **http://127.0.0.1:8000/login/**

---

## 🔐 Demo Login Credentials

> These accounts were created via the Supabase MCP server during project setup.

| Role | Username | Password | Access |
|---|---|---|---|
| 🔴 **Principal** (Super Admin) | `admin` | `Admin@123` | Full admin dashboard, analytics, approve/reject all events |
| 🔵 **Student** | `testuser1` | `password123` | Register for events, take assessments, download certificates |

### Create your own account
Visit **http://127.0.0.1:8000/register/** and fill in the form.  
Select your role from: `Student`, `Event Coordinator`, `HOD`, or `Principal`.

### Django Admin Panel
Access the full admin panel at **http://127.0.0.1:8000/admin/**
- **Username:** `admin`
- **Password:** `Admin@123`

---

## ✨ Features

### 🗂 Event Lifecycle Management
The entire event lifecycle is managed through a multi-level approval chain:

```
Event Coordinator Creates Event
         ↓
   HOD Reviews & Approves
         ↓
 Principal Reviews & Approves
         ↓
 Event Published to Students
```

- **Create & Edit Events** — Coordinators submit online/offline events with full budget, schedule, and resource details.
- **HOD Approval** — Department Heads review and approve/reject events with reasons.
- **Principal Approval** — Final sign-off; Principal has a global view of all events.
- **Rejection Reasons** — Rejection always includes a reason visible to the coordinator.

---

### 📊 Analytics Dashboard
- **Event statistics** — total events, approved, pending, budgets
- **Department breakdown** — per-department event counts and average attendees
- **Chart.js** visualizations with bar and doughnut charts
- Available to **HOD** (department-filtered) and **Principal** (global view)

---

### 📝 Assessments & Grading
- Coordinators create **custom quizzes** for events with MCQ and numerical questions.
- Students **take assessments** after attending events.
- AI-assisted grading for numerical answers (`events/ai_assessment.py`)
- Coordinators can view **submission reports** and manually grade answers.
- Students see their **assessment results** and scores.

---

### 🏅 Certificates
- Automatic **PDF certificate generation** for students who attended approved events.
- Uses **ReportLab** + **Pillow** for high-quality PDF output.
- Includes **QR code** on each certificate for verification.
- Students download certificates directly from their dashboard.

---

### 👤 Role-Based Access Control

| Feature | Student | Coordinator | HOD | Principal |
|---|:---:|:---:|:---:|:---:|
| Browse Events | ✅ | | | |
| Register for Events | ✅ | | | |
| Take Assessments | ✅ | | | |
| Download Certificates | ✅ | | | |
| Create Events | | ✅ | | |
| Manage Own Events | | ✅ | | |
| Create Assessments | | ✅ | | |
| Approve (Dept.) Events | | | ✅ | |
| View Dept. Analytics | | | ✅ | |
| Final Event Approval | | | | ✅ |
| View All Analytics | | | | ✅ |
| Django Admin | | | | ✅ |

---

### 🔒 Security Features
- **Session timeout** — Sessions expire after 30 minutes of inactivity
- **CSRF protection** — Django's built-in CSRF middleware
- **LocalhostOnly middleware** — Restricts access to localhost in dev
- **WhiteNoise** — Secure static file serving in production
- **Environment-based DEBUG** — `DEBUG=False` when deployed to Render

---

## 🌐 Cloud Database (Supabase)

This project uses **Supabase PostgreSQL** for the production database.

- **Project name:** `cems-db`
- **Region:** `ap-south-1` (Mumbai)
- **Project URL:** `https://ojfyotnxnmbomzhdpuxd.supabase.co`

To connect, set the `DATABASE_URL` environment variable in Render:
```
postgresql://postgres:[YOUR-PASSWORD]@db.ojfyotnxnmbomzhdpuxd.supabase.co:5432/postgres
```
*(Get the full connection string from [Supabase Dashboard → cems-db → Connect](https://supabase.com/dashboard/project/ojfyotnxnmbomzhdpuxd/settings/database))*

---

## 🚢 Deploy to Render

1. Push your code to GitHub.
2. Go to [Render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repository.
4. Fill in:
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn dems.wsgi:application`
5. Add environment variables:
   - `DATABASE_URL` = *(Supabase connection string)*
   - `RENDER` = `true`

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Django 5.0.1 |
| Database (local) | SQLite3 |
| Database (production) | Supabase PostgreSQL |
| Frontend | Bootstrap 4, Chart.js |
| Forms | django-crispy-forms + crispy-bootstrap4 |
| Analytics | scikit-learn, pandas, matplotlib, seaborn |
| PDF Generation | ReportLab, Pillow |
| Certificate QR | qrcode |
| SVG Rendering | CairoSVG |
| Web Server | Gunicorn |
| Static Files | WhiteNoise |
| Session Management | django-session-timeout |

---

## 📁 Project Structure

```
cems/
├── dems/                  # Django project package
│   ├── settings.py        # Project settings (dj-database-url, whitenoise)
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py
├── users/                 # Custom user authentication app
│   ├── models.py          # CustomUser with role & department
│   ├── views.py           # Login, register, profile, dashboard
│   ├── middleware.py      # LocalhostOnly & FileIntegrity middleware
│   └── templates/users/
│       ├── base.html      # Shared layout with sidebar
│       ├── login.html
│       ├── register.html
│       └── dashboard.html
├── events/                # Core event management app
│   ├── models.py          # Event, Assessment, Submission, etc.
│   ├── views.py           # All event views (create, approve, assess)
│   ├── dashboard_api.py   # Analytics API endpoints
│   ├── ai_assessment.py   # AI-powered assessment grading
│   ├── utils.py           # Certificate, QR, PDF generation
│   └── templates/events/
│       ├── my_events.html
│       ├── create_event.html
│       ├── event_detail.html
│       ├── available_events.html
│       ├── analytics.html
│       ├── hod_pending_events.html
│       ├── certificates.html
│       └── ... more templates
├── static/                # Static assets
├── staticfiles/           # Collected static files (production)
├── build.sh               # Render deployment script
├── requirements.txt
├── manage.py
└── .gitignore
```

---

<div align="center">
Made with ❤️ by CMRIT Students &nbsp;|&nbsp; Powered by Django + Supabase
</div>
