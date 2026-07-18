# Retail Sales Intelligence Platform

> A full-stack analytics platform for retail businesses to make data-driven decisions using sales data analysis, interactive dashboards, SQL analytics, and machine learning forecasting.

**[Full Documentation →](docs/README.md)** · **[API Reference →](docs/API_DOCUMENTATION.md)** · **[Setup Guide →](docs/SETUP_GUIDE.md)** · **[Interview Guide →](docs/INTERVIEW_GUIDE.md)**

---

## Features

- 🔐 **Authentication** — JWT login/register with bcrypt password hashing
- 📊 **ETL Pipeline** — CSV upload, validation, cleaning, and feature engineering
- 📈 **SQL Analytics** — 10+ parameterized queries for business intelligence
- 🤖 **ML Forecasting** — Random Forest model with feature importance and evaluation metrics
- 💡 **Business Insights** — Automated actionable recommendations
- 📑 **Report Export** — Downloadable CSV and PDF reports

## Tech Stack

**Backend**: FastAPI · SQLAlchemy · PostgreSQL · Pandas · Scikit-learn  
**Frontend**: React · Tailwind CSS · Recharts · Lucide Icons  
**Auth**: JWT · bcrypt  
**ML**: Random Forest Regressor  

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
python seed_data.py
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

**Test Account**: test@example.com / password123

See the full [Setup Guide](docs/SETUP_GUIDE.md) for detailed instructions.

## Architecture

See [Architecture Documentation](docs/ARCHITECTURE.md) and [Database Design](docs/DATABASE_DESIGN.md) for detailed technical explanations.

## License

Academic portfolio project. Not intended for commercial use.
