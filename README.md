# Retail Sales Intelligence Platform

A full-stack retail analytics platform that enables businesses to analyze sales performance, generate business insights, and forecast future sales using machine learning.

**Live Demo:** https://retail-sales-intelligence.vercel.app

**Documentation:** [Project Documentation](docs/README.md) · [API Reference](docs/API_DOCUMENTATION.md) · [Setup Guide](docs/SETUP_GUIDE.md) · [Interview Guide](docs/INTERVIEW_GUIDE.md)

---

## Features

- Secure user authentication using JWT and bcrypt
- CSV upload with data validation, cleaning, and preprocessing
- Interactive dashboards for sales analysis and visualization
- SQL-based business analytics using parameterized queries
- Machine learning sales forecasting using Random Forest
- Automated business insights and recommendations
- Export reports in CSV and PDF formats

---

## Technology Stack

### Frontend
- React
- Tailwind CSS
- Recharts
- Axios

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL (Supabase)

### Machine Learning
- Pandas
- NumPy
- Scikit-learn

### Authentication
- JWT
- Passlib (bcrypt)

### Deployment
- Frontend: Vercel
- Backend: Render
- Database: Supabase PostgreSQL

---

## Live Application

https://retail-sales-intelligence.vercel.app

---

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python seed_data.py
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Test Account

**Email:** test@example.com

**Password:** password123

---

## Project Structure

```
Retail-Sales-Intelligence/
│
├── backend/
│   ├── routers/
│   ├── services/
│   ├── middleware/
│   ├── models/
│   ├── schemas/
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── docs/
│   ├── README.md
│   ├── API_DOCUMENTATION.md
│   ├── ARCHITECTURE.md
│   ├── DATABASE_DESIGN.md
│   ├── INTERVIEW_GUIDE.md
│   └── SETUP_GUIDE.md
│
└── README.md
```

---

## Documentation

Additional documentation is available in the `docs` directory.

- [Project Documentation](docs/README.md)
- [API Reference](docs/API_DOCUMENTATION.md)
- [Architecture Documentation](docs/ARCHITECTURE.md)
- [Database Design](docs/DATABASE_DESIGN.md)
- [Setup Guide](docs/SETUP_GUIDE.md)
- [Interview Guide](docs/INTERVIEW_GUIDE.md)

---

## License

This project was developed as an academic portfolio project and is intended for learning and demonstration purposes.
