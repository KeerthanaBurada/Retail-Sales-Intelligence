# Setup Guide

Step-by-step instructions to run the Retail Sales Intelligence Platform on your local machine.

---

## Prerequisites

### Software Requirements
| Software | Version | Download |
|----------|---------|----------|
| Python | 3.10 or higher | [python.org](https://python.org) |
| Node.js | 18 or higher | [nodejs.org](https://nodejs.org) |
| PostgreSQL | 14 or higher | [postgresql.org](https://www.postgresql.org/download/) |
| Git | Any recent version | [git-scm.com](https://git-scm.com) |

### Verify Installation
```bash
python --version    # Should show 3.10+
node --version      # Should show 18+
psql --version      # Should show 14+
```

> **Windows Users**: Make sure Python and PostgreSQL are added to your system PATH during installation. Check "Add Python to PATH" in the Python installer.

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/retail-intelligence-platform.git
cd retail-intelligence-platform
```

---

## Step 2: Set Up PostgreSQL

### Create the Database

**Option A: Using psql command line**
```bash
# Connect to PostgreSQL
psql -U postgres

# Create the database
CREATE DATABASE retail_intelligence;

# Verify it was created
\l

# Exit
\q
```

**Option B: Using pgAdmin**
1. Open pgAdmin
2. Right-click "Databases" → "Create" → "Database"
3. Name: `retail_intelligence`
4. Click "Save"

### Common Issue: PostgreSQL Authentication

If you get a password authentication error:

1. Find `pg_hba.conf` (usually in PostgreSQL's data directory)
2. Change `md5` to `trust` for local connections (development only)
3. Restart PostgreSQL service

**Windows**: Services → PostgreSQL → Restart

---

## Step 3: Set Up the Backend

### Navigate to backend directory
```bash
cd backend
```

### Create a virtual environment (recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Install Python dependencies
```bash
pip install -r requirements.txt
```

### Configure environment variables
```bash
# Copy the example env file
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials:
```
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/retail_intelligence
SECRET_KEY=any-random-string-for-development
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

### Seed the database with sample data
```bash
python seed_data.py
```

This will:
- Create all database tables
- Generate ~5,000 realistic sales records
- Create a test user account
- Print summary statistics

**Expected output:**
```
Creating database tables...
Generating seed data...
Created test user: test@example.com / password123
Generated 5000 sales records
Seed data inserted successfully!
```

### Start the backend server
```bash
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Verify backend is running
Open http://localhost:8000/docs in your browser. You should see the FastAPI Swagger documentation.

---

## Step 4: Set Up the Frontend

### Open a new terminal and navigate to frontend
```bash
cd frontend
```

### Install Node.js dependencies
```bash
npm install
```

### Start the development server
```bash
npm run dev
```

The frontend will be available at http://localhost:5173

---

## Step 5: Access the Application

1. Open http://localhost:5173 in your browser
2. Login with the test account:
   - **Email**: test@example.com
   - **Password**: password123
3. The dashboard should load with pre-seeded data

---

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'xxx'"
```bash
# Make sure your virtual environment is activated
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### "psycopg2 installation fails on Windows"
The `requirements.txt` uses `psycopg2-binary` which includes pre-compiled binaries. If it still fails:
```bash
pip install psycopg2-binary --no-cache-dir
```

#### "Connection refused" when starting backend
- Verify PostgreSQL is running: `pg_isready` (should say "accepting connections")
- Check your DATABASE_URL in `.env`
- Make sure the database `retail_intelligence` exists

#### "CORS error" in browser console
- Make sure the backend is running on port 8000
- Check that the frontend URL (http://localhost:5173) is in the CORS allow list in `main.py`

#### "Port 8000 already in use"
```bash
# Windows: Find and kill the process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use a different port:
uvicorn main:app --port 8001
```

#### "npm ERR! could not determine executable to run"
```bash
# Clear npm cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Frontend shows blank page
- Check browser console for errors (F12 → Console)
- Verify the backend is running and accessible
- Try clearing localStorage: `localStorage.clear()` in browser console

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | postgresql://postgres:password@localhost:5432/retail_intelligence | PostgreSQL connection string |
| SECRET_KEY | Yes | dev-secret-key-change-me | JWT signing secret |
| ACCESS_TOKEN_EXPIRE_MINUTES | No | 480 | Token expiration (8 hours) |

---

## Development Tips

### Running Backend with Auto-Reload
```bash
python main.py
# or
uvicorn main:app --reload --port 8000
```

### Resetting the Database
```bash
# Drop and recreate
psql -U postgres -c "DROP DATABASE retail_intelligence;"
psql -U postgres -c "CREATE DATABASE retail_intelligence;"

# Re-seed
python seed_data.py
```

### Checking API Endpoints
Use the Swagger UI at http://localhost:8000/docs to test endpoints directly. You can authenticate by clicking "Authorize" and entering a JWT token.
