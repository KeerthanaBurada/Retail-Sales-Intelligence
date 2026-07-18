# Retail Sales Intelligence Platform

A full-stack analytics platform that helps retail businesses make data-driven decisions using sales data analysis, interactive dashboards, SQL analytics, and machine learning forecasting.

Built as a capstone project demonstrating skills in **Data Engineering**, **SQL Analytics**, **Machine Learning**, **Backend Development**, and **Dashboard Design**.

---

## What Does This Project Do?

Imagine you're a retail chain manager with thousands of sales transactions across multiple regions, categories, and customer segments. You need answers to questions like:

- *Which region is underperforming and why?*
- *What products should we stock more of next quarter?*
- *Are our profit margins healthy across all categories?*
- *What will our sales look like in the next 6 months?*

This platform takes raw sales data (CSV uploads), cleans and processes it through an ETL pipeline, stores it in PostgreSQL, and provides:

1. **Interactive Dashboards** — KPIs, charts, and trends at a glance
2. **SQL-Powered Analytics** — Deep-dive analysis by region, category, customer segment
3. **ML Sales Forecasting** — Random Forest model predicting future sales
4. **Business Insights** — Automated actionable recommendations
5. **Exportable Reports** — Download analysis as CSV or PDF

---

## Tech Stack

| Layer | Technology | Why This Choice |
|-------|-----------|-----------------|
| **Frontend** | React, Tailwind CSS, Recharts | Modern UI with fast charting |
| **Backend** | FastAPI, SQLAlchemy, Pydantic | High-performance async Python API |
| **Database** | PostgreSQL | Robust SQL analytics, ACID compliance |
| **Data Engineering** | Pandas, NumPy | Industry-standard data manipulation |
| **Machine Learning** | Scikit-learn (Random Forest) | Reliable, interpretable predictions |
| **Auth** | JWT + bcrypt | Stateless, secure authentication |
| **Reports** | ReportLab | PDF generation for business reports |

---

## Features

### Authentication
- JWT-based login and registration
- Password hashing with bcrypt
- Protected API routes
- Persistent sessions via localStorage

### ETL Pipeline (Data Engineering)
- CSV file upload with drag-and-drop
- Column validation and standardization
- Missing value handling (median for numeric, mode for categorical)
- Duplicate removal
- Feature engineering (profit margin, processing days, temporal features)
- Detailed upload statistics and error reporting

### SQL Analytics
- **KPI Dashboard**: Revenue, profit, orders, AOV, margin, unique customers
- **Monthly Revenue Trends**: Identify seasonality and growth
- **Top Products & Customers**: Revenue ranking with segmentation
- **Regional Analysis**: Performance comparison across East, West, Central, South
- **Category Performance**: Revenue, profit, and margin by product category
- **Customer Segmentation**: Consumer vs Corporate vs Home Office analysis
- **State-Level Breakdown**: Granular geographic analysis
- All queries use parameterized SQL to prevent injection

### Machine Learning
- **Random Forest Regressor** for sales prediction
- Feature engineering from temporal, categorical, and numerical attributes
- Model evaluation: RMSE, MAE, R² Score
- Feature importance visualization
- Actual vs Predicted comparison
- Future sales forecasting (configurable periods)
- Model persistence with joblib

### Business Insights
- Automated insight generation from analytics data
- Regional performance recommendations
- Category optimization suggestions
- Margin alerts and discount impact analysis
- Seasonal pattern detection
- Revenue trend analysis

### Reports
- Summary, forecast, and full report types
- CSV export for spreadsheet analysis
- PDF export with formatted tables and insights
- Report history and management

---

## Project Structure

```
retail-intelligence-platform/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Environment configuration
│   ├── database.py             # SQLAlchemy database setup
│   ├── seed_data.py            # Generate sample retail dataset
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── user.py             # User authentication model
│   │   ├── dataset.py          # Dataset and SalesRecord models
│   │   └── forecast.py         # ForecastResult and SavedReport models
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── user.py             # Auth schemas
│   │   ├── dataset.py          # Dataset schemas
│   │   ├── analytics.py        # Analytics response schemas
│   │   └── forecast.py         # Forecast schemas
│   ├── services/               # Business logic layer
│   │   ├── auth_service.py     # JWT and password hashing
│   │   ├── etl_service.py      # ETL pipeline (data engineering)
│   │   ├── analytics_service.py # SQL analytics queries
│   │   ├── ml_service.py       # Random Forest ML model
│   │   ├── insights_service.py # Business insight generation
│   │   └── report_service.py   # Report assembly and export
│   ├── routers/                # API route handlers
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── datasets.py         # Dataset management endpoints
│   │   ├── analytics.py        # Analytics endpoints
│   │   ├── forecast.py         # ML forecast endpoints
│   │   └── reports.py          # Report endpoints
│   ├── middleware/
│   │   └── auth_middleware.py  # JWT verification dependency
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                # Axios API service modules
│   │   ├── components/         # Reusable UI components
│   │   ├── context/            # React Context (Auth)
│   │   └── pages/              # Page components
│   ├── package.json
│   └── tailwind.config.js
└── docs/
    ├── README.md               # This file
    ├── API_DOCUMENTATION.md    # Complete API reference
    ├── DATABASE_DESIGN.md      # Schema and ER diagram
    ├── ARCHITECTURE.md         # System architecture
    ├── SETUP_GUIDE.md          # Local setup instructions
    └── INTERVIEW_GUIDE.md      # Interview preparation
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Create PostgreSQL database
createdb retail_intelligence

# Copy and edit environment variables
cp .env.example .env

# Seed sample data (creates test user and ~5000 sales records)
python seed_data.py

# Start the API server
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Access
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Test Account**: test@example.com / password123

---

## Sample Dataset

The seed script generates ~5,000 realistic retail sales records modeled after the Superstore dataset:

- **Time Range**: January 2022 – December 2023
- **Regions**: East, West, Central, South (with US states)
- **Categories**: Furniture, Office Supplies, Technology
- **Customer Segments**: Consumer, Corporate, Home Office
- **Metrics**: Sales, Quantity, Discount, Profit

The data includes realistic seasonal patterns (Q4 holiday spike), category-specific pricing, and discount-driven margin variations.

---

## Key Design Decisions

1. **FastAPI over Flask/Django**: Async-ready, automatic OpenAPI docs, Pydantic validation built-in
2. **Random Forest over LSTM**: Better suited for tabular data with ~5000 rows; interpretable feature importance
3. **SQLAlchemy text() queries**: Raw SQL for analytics gives full control over complex aggregations while parameterized queries prevent SQL injection
4. **JWT over sessions**: Stateless auth scales better; no server-side session storage needed
5. **Pandas ETL over Spark**: Right tool for the data size; Spark would be overengineering for < 100K rows

---

## License

This project is part of an academic portfolio. Not intended for commercial use.
