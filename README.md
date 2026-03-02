# 🎓 CEMS — Campus Event Management System

<div align="center">

![Django](https://img.shields.io/badge/Django-5.0.1-green?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-47A248?style=for-the-badge&logo=mongodb)
![Bootstrap](https://img.shields.io/badge/UI-Bootstrap_4-purple?style=for-the-badge&logo=bootstrap)

**A full-stack Django web application for managing campus events, approvals, assessments, and certificates.**

*Built for CMR Institute of Technology, Bengaluru.*

</div>

---

## 🚀 Quick Start — Run Locally

### Prerequisites
- Python 3.10+
- MongoDB 6+ running on `localhost:27017`
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

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env if needed — defaults work for local MongoDB
```

### 5. Run setup (Django sessions + seed demo users)
```bash
python manage.py migrate --run-syncdb
python manage.py seed_users
```

### 6. Start the development server
```bash
python manage.py runserver
```

Open your browser and go to **http://127.0.0.1:8000/login/**

---

## 🔐 Demo Login Credentials

| Role | Username | Password | Access |
|---|---|---|---|
| 🔴 **Principal** (Admin) | `admin` | `Admin@123` | Full analytics, approve/reject all events |
| 🔵 **Student** | `testuser1` | `password123` | Register for events, take assessments, download certificates |

### Create your own account
Visit **http://127.0.0.1:8000/register/** and fill in the form.  
Select your role from: `Student`, `Event Coordinator`, `HOD`, or `Principal`.

---

## ✨ Features

### 🗂 Event Lifecycle Management
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

---

### 📊 Analytics Dashboard
- **Event statistics** — total events, approved, pending, budgets
- **Department breakdown** — per-department event counts
- **Chart.js** visualizations with bar and doughnut charts
- Available to **HOD** (department-filtered) and **Principal** (global view)

---

### 📝 Assessments & Grading
- Coordinators create **custom quizzes** for events with MCQ, MSQ, and NAT questions.
- Students **take assessments** after attending events.
- AI-assisted grading for all question types.
- Coordinators can view **submission reports** and manually grade answers.

---

### 🏅 Certificates
- Automatic **PDF certificate generation** for students who passed assessments.
- Uses **ReportLab** + **Pillow** for high-quality PDF output.
- Includes **QR code** on each certificate for verification.

---

## 🌐 Cloud Database (MongoDB Atlas)

This project uses **MongoDB Atlas** for the production database.

1. Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a database named **`eventwebsite`**
3. Get your connection string:
```
mongodb+srv://<username>:<password>@<cluster>.mongodb.net/eventwebsite?retryWrites=true&w=majority
```
4. Set it as `MONGODB_URI` on Render (see below).

---

## 🚢 Deploy to Render

1. Push your code to GitHub.
2. Go to [Render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repository.
4. Fill in:
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn dems.wsgi:application`
5. Add environment variables:
   - `MONGODB_URI` = *(MongoDB Atlas connection string pointing to `eventwebsite` database)*
   - `RENDER` = `true`
   - `SECRET_KEY` = *(a strong random secret key)*

The `build.sh` script will automatically:
- Install dependencies
- Collect static files
- Create Django session tables (SQLite)
- Seed demo users (`admin` / `Admin@123` and `testuser1` / `password123`) into MongoDB

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Django 5.0.1 |
| Database | MongoDB (MongoEngine ODM) |
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
│   ├── settings.py        # Project settings (MongoDB, whitenoise)
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py
├── users/                 # Custom user authentication app
│   ├── models.py          # CustomUser (MongoEngine Document)
│   ├── backends.py        # Custom MongoDB auth backend
│   ├── views.py           # Login, register, profile, dashboard
│   ├── middleware.py      # MongoAuthMiddleware
│   └── management/commands/seed_users.py
├── events/                # Core event management app
│   ├── models.py          # Event, Assessment, Submission, etc. (MongoEngine)
│   ├── views.py           # All event views
│   ├── dashboard_api.py   # Analytics API endpoints
│   ├── ai_assessment.py   # AI-powered assessment grading
│   └── utils.py           # Certificate, QR, PDF generation
├── static/                # Static assets
├── staticfiles/           # Collected static files (production)
├── build.sh               # Render deployment script
├── .env.example           # Environment variable template
├── requirements.txt
└── manage.py
```

---

<div align="center">
Made with ❤️ by CMRIT Students &nbsp;|&nbsp; Powered by Django + MongoDB
</div>
