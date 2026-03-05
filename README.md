# 🌾 Crop Management DBMS

A comprehensive database management system for agricultural field management with satellite data integration.

## 📊 Features

- ✅ User authentication (JWT)
- ✅ Field management (CRUD)
- ✅ Crop cycle tracking
- ✅ Satellite observation data (1,599+ records)
- ✅ Weather tracking
- ✅ Alerts & monitoring
- ✅ FastAPI with auto-documentation

## 🗄️ Database

- **PostgreSQL** - Production database
- **1,599 records** - Seeded with agricultural data
- **10 tables** - Users, Regions, Fields, Crop Cycles, Observations, etc.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 18+
- pip

### Installation

1. **Clone the repo:**
```bash
   git clone https://github.com/YOUR_USERNAME/crop-management-dbms.git
   cd DBMS
```

2. **Create virtual environment:**
```bash
   python -m venv venv
   venv\Scripts\activate
```

3. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

4. **Setup database:**
   - Create PostgreSQL database: `cropdb`
   - Update `.env` with your database credentials
   - Run: `python seed.py`

5. **Run the API:**
```bash
   python main.py
```

6. **Test the API:**
   - Open: http://localhost:5000/docs

## 📁 Project Structure
```
DBMS/
├── main.py                 # FastAPI entry point
├── database.py             # Database configuration
├── models.py               # SQLAlchemy models (10 tables)
├── schemas.py              # Pydantic validation schemas
├── auth.py                 # Authentication service
├── seed.py                 # Database seeding script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── .gitignore              # Git ignore rules
├── Data/                   # CSV files for seeding
│   ├── users.csv
│   ├── fields.csv
│   ├── crop_cycles.csv
│   └── ... (7 more CSVs)
└── routes/
    ├── __init__.py
    ├── auth.py             # Authentication endpoints
    ├── users.py            # User CRUD endpoints
    ├── fields.py           # Field CRUD endpoints
    └── crop_cycles.py      # Crop cycle endpoints
```

## 📊 Database Schema

| Table | Records | Purpose |
|-------|---------|---------|
| users | 20 | User accounts |
| regions | 8 | Geographic regions (Punjab, Sindh, etc.) |
| fields | 50 | Agricultural fields |
| crop_cycles | 75 | Growing seasons |
| satellites | 5 | Satellite sources |
| observations | 162 | Satellite observations |
| band_values | 644 | Spectral band data |
| weather_records | 1000 | Weather data |
| derived_metrics | 116 | NDVI, EVI, etc. |
| alerts | 120 | System alerts |

## 🔐 API Endpoints

### Authentication
```
POST   /api/auth/register     - Register new user
POST   /api/auth/login        - Login and get JWT token
GET    /api/auth/test         - Test auth routes
```

### Users
```
GET    /api/users/            - Get all users
GET    /api/users/{id}        - Get specific user
PUT    /api/users/{id}        - Update user
DELETE /api/users/{id}        - Delete user
```

### Fields
```
GET    /api/fields/           - Get all fields
GET    /api/fields/{id}       - Get specific field
POST   /api/fields/           - Create field
PUT    /api/fields/{id}       - Update field
DELETE /api/fields/{id}       - Delete field
```

### Crop Cycles
```
GET    /api/crop-cycles/field/{field_id}  - Get field cycles
GET    /api/crop-cycles/{id}              - Get specific cycle
POST   /api/crop-cycles/                  - Create cycle
PUT    /api/crop-cycles/{id}              - Update cycle
DELETE /api/crop-cycles/{id}              - Delete cycle
```

## 🔗 Interactive API Documentation

Visit **http://localhost:5000/docs** for Swagger UI documentation

## 👥 Team

- **Your Name** - Backend Development

## 📝 Notes

- Database seeded with 1,599 agricultural records
- JWT authentication with 24-hour token expiry
- CORS enabled for frontend integration
- All CRUD operations tested and working

## 🔄 Workflow

1. Create a branch: `git checkout -b feature/your-feature`
2. Make changes and commit: `git commit -m "description"`
3. Push: `git push origin feature/your-feature`
4. Create Pull Request on GitHub

