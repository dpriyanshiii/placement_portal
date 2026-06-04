# Placement Portal App

A web application that connects students, companies, and institute admins for managing campus placement drives. Built with Flask and SQLite.

---

## Features

**Admin (Institute)**
- Approve or reject company registrations
- Blacklist students or companies
- View all students, companies, and placement drives
- Access full application details

**Companies**
- Register and set up a company profile (with logo upload)
- Create and manage placement drives
- Review student applications and update their status (shortlist / reject)

**Students**
- Register with profile details and upload a resume (PDF)
- Browse active placement drives and company listings
- Apply to drives and track application history

---

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite via Flask-SQLAlchemy
- **Auth:** Session-based login with Werkzeug password hashing
- **Frontend:** Jinja2 templates (HTML)
- **File uploads:** Resumes (PDF), company logos (PNG/JPG)

---

## Project Structure

```
placement-portal-app/
├── app.py                  # App factory, config, blueprint registration
├── models.py               # DB models: User, Student, Company, PlacementDrive, Application
├── extensions.py           # SQLAlchemy instance
├── routes/
│   ├── auth.py             # Login, signup (student & company)
│   ├── admin.py            # Admin dashboard and management routes
│   ├── company.py          # Company dashboard, drives, applications
│   └── student.py          # Student dashboard, apply, history
├── templates/
│   ├── auth/
│   ├── admin/
│   ├── company/
│   └── student/
└── static/
    └── uploads/
        ├── resumes/
        └── logos/
```

---

## Getting Started

### Prerequisites

- Python 3.x
- pip

### Installation

1. Clone the repository or extract the zip:
   ```bash
   git clone <repo-url>
   cd placement-portal-app
   ```

2. Install dependencies:
   ```bash
   pip install flask flask-sqlalchemy werkzeug
   ```

3. Run the app:
   ```bash
   python app.py
   ```
   This will create the SQLite database and a default admin user on first run.

4. Open your browser at `http://127.0.0.1:5000`

### Default Admin Credentials

| Field    | Value                          |
|----------|-------------------------------|
| Email    | `24f3001002@ds.study.iitm.ac.in` |
| Password | `password1526`                 |

> **Important:** Change the `SECRET_KEY` in `app.py` and update the admin credentials before deploying.

---

## User Roles

| Role    | Registration         | Notes                                      |
|---------|----------------------|--------------------------------------------|
| Admin   | Pre-created on setup | One admin, manages the whole portal        |
| Company | Self-register        | Must be approved by admin before logging in |
| Student | Self-register        | Can apply to active drives immediately     |

---

## Notes

- The database file (`instance/placementapp.db`) is created automatically on first run.
- Uploaded files are stored in `static/uploads/resumes/` and `static/uploads/logos/`.
- Drive deadlines are checked automatically on the student dashboard — expired drives are marked as closed.