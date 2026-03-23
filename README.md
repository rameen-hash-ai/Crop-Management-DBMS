# 🌾 Crop Management DBMS API

A FastAPI-based agricultural field management system with Role-Based Access Control (RBAC).

---

## 📋 Prerequisites

Make sure you have these installed before starting:

- [Python 3.10+](https://www.python.org/downloads/)
- [PostgreSQL 14+](https://www.postgresql.org/download/)
- [Git](https://git-scm.com/)
- [pgAdmin](https://www.pgadmin.org/) (optional but recommended)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <repo-folder>
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv bcrypt python-jose[cryptography] pydantic[email]
```

Or if a `requirements.txt` exists:

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

Open pgAdmin or psql and run:

```sql
CREATE DATABASE crop_db;
```

### 5. Create the `.env` File

Create a file named `.env` in the root of the project:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/crop_db
SECRET_KEY=your-secret-key-change-this
```

> ⚠️ Replace `YOUR_PASSWORD` with your PostgreSQL password.  
> ⚠️ Never commit `.env` to Git — it's already in `.gitignore`.

### 6. Create the Database Tables

Run this once to create all tables:

```bash
python seed.py
```

### 7. Add Missing Columns (if importing existing data from CSV)

If you imported data from CSV files previously, run this in pgAdmin Query Tool to fix auto-increment sequences and add new columns:

```sql
-- Add missing columns
ALTER TABLE fields ADD COLUMN IF NOT EXISTS field_name VARCHAR(150);
ALTER TABLE fields ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE fields ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();

ALTER TABLE crop_cycle ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active';
ALTER TABLE crop_cycle ADD COLUMN IF NOT EXISTS actual_harvest_date VARCHAR(20);
ALTER TABLE crop_cycle ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();

ALTER TABLE satellite ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
ALTER TABLE weather ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
ALTER TABLE observation ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();

-- Fix auto-increment sequences (run if you imported data from CSV)
SELECT setval('users_user_id_seq', (SELECT MAX(user_id) FROM users));
SELECT setval('fields_field_id_seq', (SELECT MAX(field_id) FROM fields));
SELECT setval('region_region_id_seq', (SELECT MAX(region_id) FROM region));
SELECT setval('satellite_satellite_id_seq', (SELECT MAX(satellite_id) FROM satellite));
SELECT setval('crop_cycle_cycle_id_seq', (SELECT MAX(cycle_id) FROM crop_cycle));
SELECT setval('weather_weather_id_seq', (SELECT MAX(weather_id) FROM weather));
SELECT setval('observation_observation_id_seq', (SELECT MAX(observation_id) FROM observation));
SELECT setval('bandvalues_band_id_seq', (SELECT MAX(band_id) FROM bandvalues));
SELECT setval('derived_metrics_metric_id_seq', (SELECT MAX(metric_id) FROM derived_metrics));
SELECT setval('alert_alert_id_seq', (SELECT MAX(alert_id) FROM alert));
```

### 8. Start the Server

```bash
uvicorn main:app --reload --port 5000
```

The API will be running at: `http://localhost:5000`  
Swagger docs at: `http://localhost:5000/docs`

---

## 📁 Project Structure

```
project/
├── main.py              # FastAPI app entry point
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic request/response schemas
├── auth.py              # Authentication & RBAC logic
├── database.py          # Database connection & session
├── seed.py              # Creates database tables
├── .env                 # Environment variables (DO NOT COMMIT)
└── routes/
    ├── auth.py          # Login & Register
    ├── users.py         # User management
    ├── regions.py       # Region management
    ├── fields.py        # Field management
    ├── crop_cycles.py   # Crop cycle management
    ├── satellites.py    # Satellite management
    ├── observations.py  # Observation management
    ├── weather.py       # Weather data
    ├── alerts.py        # Alert management
    ├── band_values.py   # Band values
    └── derived_metrics.py # Derived metrics (NDVI, EVI etc.)
```

---

## 🔐 Authentication

The API uses JWT Bearer tokens. Every protected route requires a token.

### Step 1 — Register a user

`POST /api/auth/register`

```json
{
  "name": "John Farmer",
  "email": "john@example.com",
  "password": "farm1234",
  "role": "farmer"
}
```

Available roles: `farmer`, `agronomist`, `admin`

### Step 2 — Login

`POST /api/auth/login`

```json
{
  "email": "john@example.com",
  "password": "farm1234"
}
```

Copy the `access_token` from the response.

### Step 3 — Authorize in Swagger

1. Go to `http://localhost:5000/docs`
2. Click the green **Authorize 🔒** button (top right)
3. Paste your token in the **Value** field
4. Click **Authorize** → **Close**

All routes will now include your token automatically.

---

## 👥 Role Permissions

| Resource         | Admin | Agronomist | Farmer |
|-----------------|-------|------------|--------|
| Users           | CRUD  | Read       | Read (own) |
| Regions         | CRUD  | Read       | Read |
| Fields          | CRUD  | Read/Update | Read/Update (own) |
| Crop Cycles     | CRUD  | Create/Read/Update | Read/Update (own) |
| Satellites      | CRUD  | Read       | Read |
| Observations    | CRUD  | Read       | Read (own) |
| Band Values     | CRUD  | Read       | Read |
| Weather         | CRUD  | Read       | Read (own) |
| Derived Metrics | CRUD  | Read       | Read |
| Alerts          | CRUD  | Create/Read/Update | Read (own) |

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get token |
| GET | `/api/users/` | Get all users |
| GET | `/api/regions/` | Get all regions |
| GET | `/api/fields/` | Get all fields |
| GET | `/api/crop-cycles/` | Get all crop cycles |
| GET | `/api/satellites/` | Get all satellites |
| GET | `/api/observations/` | Get all observations |
| GET | `/api/weather/` | Get all weather records |
| GET | `/api/alerts/` | Get all alerts |
| GET | `/api/band-values/` | Get all band values |
| GET | `/api/derived-metrics/` | Get all derived metrics |

Full endpoint list available at `/docs`.

---

## ⚠️ Common Issues

**`Key (user_id)=(1) already exists`**  
You imported CSV data and the sequence is out of sync. Run the sequence fix SQL from Step 7.

**`column fields.field_name does not exist`**  
Run the ALTER TABLE statements from Step 7 to add missing columns.

**`401 Unauthorized`**  
You forgot to authorize in Swagger. Follow the Authentication steps above.

**`422 Unprocessable Content`**  
Your request body is missing a required field or has wrong format. Check Swagger for the exact error detail.

**`ModuleNotFoundError`**  
Your virtual environment is not activated. Run `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux).

---

## 🛠️ Tech Stack

- **FastAPI** — Web framework
- **SQLAlchemy** — ORM
- **PostgreSQL** — Database
- **Pydantic** — Data validation
- **bcrypt** — Password hashing
- **python-jose** — JWT tokens
- **uvicorn** — ASGI server