# Assessment Platform Starter

Full-stack starter application featuring:
- **Frontend**: React + Vite (located in `app/client`)
- **Backend**: Python Django REST Framework (located in `app/server`)

---

## Project Structure

```text
Assesment-plateform/
├── app/
│   ├── client/               # React + Vite frontend
│   │   ├── src/
│   │   │   ├── App.jsx       # Interactive starter dashboard
│   │   │   ├── App.css
│   │   │   └── main.jsx
│   │   └── package.json
│   └── server/               # Django REST Framework backend
│       ├── api/              # REST API application
│       │   ├── models.py     # Assessment model
│       │   ├── serializers.py# DRF Serializers
│       │   ├── views.py      # Health check and ViewSets
│       │   └── urls.py       # API endpoints routing
│       ├── config/           # Django project configuration
│       │   ├── settings.py   # Configured for DRF & CORS
│       │   └── urls.py
│       ├── manage.py
│       ├── requirements.txt
│       └── venv/             # Python virtual environment
└── README.md
```

---

## Quick Start

### 1. Start Backend (Django REST Framework)

Open a terminal and navigate to `app/server`:

```powershell
cd "d:\Projects\Live Projects\Assesment-plateform\app\server"
.\venv\Scripts\python manage.py runserver
```

The REST API will be available at:
- **Health Check**: [http://127.0.0.1:8000/api/health/](http://127.0.0.1:8000/api/health/)
- **Assessments API**: [http://127.0.0.1:8000/api/assessments/](http://127.0.0.1:8000/api/assessments/)
- **Django Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

*(Optional)* Create a Django superuser for the admin portal:
```powershell
.\venv\Scripts\python manage.py createsuperuser
```

---

### 2. Start Frontend (React + Vite)

Open a separate terminal and navigate to `app/client`:

```powershell
cd "d:\Projects\Live Projects\Assesment-plateform\app\client"
npm run dev
```

The frontend will be running at [http://localhost:5173/](http://localhost:5173/).

---

## Features Pre-Configured

- **CORS Handling**: `django-cors-headers` configured for Vite's `http://localhost:5173` origin.
- **REST API Endpoints**:
  - `GET /api/health/` - Server health check.
  - `GET /api/assessments/` - Retrieve all assessments.
  - `POST /api/assessments/` - Create a new assessment.
- **SQLite Database**: Initialized with automatic migrations applied and starter seed records.
- **Live React UI**: Connected to the backend with interactive status checking and data creation.
