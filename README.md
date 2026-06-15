# Placement Portal App

A web application that connects students, companies, and institute admins for managing campus placement drives. Built with Flask and SQLite, with a custom dark-themed UI layered on top of the working application.

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

**UI / Design**
- Every page extends a shared `templates/base.html` layout — sticky topbar with role badges, footer, and flash-message region
- Custom dark "editorial" theme built with plain CSS variables — no Bootstrap/Tailwind
- Playfair Display (headings) + IBM Plex Sans/Mono (body, labels, nav) via Google Fonts
- Shared components reused across all roles: page headers, stat grids, data tables, badges, forms, hero/landing layout, profile blocks, empty states

---

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite via Flask-SQLAlchemy
- **Auth:** Session-based login with Werkzeug password hashing
- **Frontend:** Jinja2 templates (HTML) extending a shared `base.html`, styled with a custom CSS design system
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
│   ├── base.html            # Shared layout, design tokens, and site-wide CSS
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
- Internet access (for Google Fonts used in the UI — Playfair Display, IBM Plex Sans/Mono)

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

## Design System

Once the core functionality (auth, CRUD, dashboards, file uploads) was working end-to-end, every template was rewritten to extend a single `templates/base.html`, which defines:

- **Design tokens** — colors, fonts, and radius set once as CSS custom properties (`--ink`, `--paper`, `--amber`, `--sage`, `--rust`, `--font-display`, `--font-body`, `--font-mono`, etc.) and reused everywhere
- **Typography** — Playfair Display for headings, IBM Plex Sans for body copy, IBM Plex Mono for labels, nav links, and badges, all loaded from Google Fonts
- **Shared chrome** — a sticky topbar with role-aware navigation and a colour-coded role badge (admin / company / student), a footer, and a flash-message region wired to Flask's `get_flashed_messages`
- **Reusable components** — page headers with a large background watermark word, stat grids/cards, data tables, status badges, form styling, the hero/landing split layout, profile hero blocks with key-value lists, and empty-state placeholders

Individual page templates now only fill in `{% block body %}` (and optionally `{% block extra_head %}` for page-specific styles or entry animations) — the surrounding layout, fonts, and base styles all come from `base.html`. This was a presentation-layer pass on top of the already-working app: no routes, models, or business logic changed as part of it.

---

## Notes

- The database file (`instance/placementapp.db`) is created automatically on first run.
- Uploaded files are stored in `static/uploads/resumes/` and `static/uploads/logos/`.
- Drive deadlines are checked automatically on the student and admin dashboards — expired drives are marked as closed.
- `templates/base.html` loads fonts from `fonts.googleapis.com` / `fonts.gstatic.com`; the UI will still work without internet access, just with fallback fonts.
