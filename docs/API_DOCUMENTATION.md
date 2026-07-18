# API Documentation

## Base URL

```
http://localhost:8000
```

All endpoints are prefixed with `/api/`. Swagger docs available at `/docs`.

---

## Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## Endpoints

### Authentication

#### POST `/api/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "email": "john@example.com",
  "name": "John Doe",
  "password": "securepass123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errors:**
- `400`: Email already registered

---

#### POST `/api/auth/login`

Authenticate an existing user.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepass123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errors:**
- `401`: Invalid email or password

---

#### GET `/api/auth/profile`

Get the current user's profile. **Protected.**

**Response (200):**
```json
{
  "id": 1,
  "email": "john@example.com",
  "name": "John Doe",
  "created_at": "2024-01-15T10:30:00"
}
```

---

### Datasets

#### POST `/api/datasets/upload`

Upload a CSV file for processing through the ETL pipeline. **Protected.**

**Request:** `multipart/form-data` with field `file` (CSV file)

**Response (200):**
```json
{
  "dataset_id": 1,
  "filename": "sales_data.csv",
  "rows_processed": 5000,
  "rows_cleaned": 4892,
  "validation_errors": [],
  "etl_stats": {
    "original_rows": 5000,
    "cleaned_rows": 4892,
    "duplicates_removed": 45,
    "missing_values_filled": 63,
    "invalid_rows_removed": 0
  }
}
```

**Errors:**
- `400`: Missing required columns or invalid file format

**Required CSV Columns:**
| Column | Type | Description |
|--------|------|-------------|
| Order ID | string | Unique order identifier |
| Order Date | date | Date the order was placed |
| Customer Name | string | Customer full name |
| Segment | string | Consumer, Corporate, or Home Office |
| City | string | City name |
| State | string | State name |
| Region | string | East, West, Central, or South |
| Category | string | Furniture, Office Supplies, or Technology |
| Sub-Category | string | Product sub-category |
| Product Name | string | Product description |
| Sales | float | Sale amount in dollars |
| Quantity | integer | Number of items |
| Discount | float | Discount percentage (0 to 1) |
| Profit | float | Profit amount in dollars |

**Optional Columns:** Ship Date, Ship Mode, Customer ID

---

#### GET `/api/datasets`

List all datasets for the current user. **Protected.**

**Response (200):**
```json
[
  {
    "id": 1,
    "filename": "sales_data.csv",
    "row_count": 4892,
    "column_count": 14,
    "status": "processed",
    "upload_stats": "{...}",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

---

#### GET `/api/datasets/{dataset_id}`

Get a single dataset's details. **Protected.**

---

#### DELETE `/api/datasets/{dataset_id}`

Delete a dataset and all associated sales records. **Protected.**

**Response (200):**
```json
{
  "message": "Dataset deleted successfully"
}
```

---

### Analytics

All analytics endpoints are **protected** and accept an optional `dataset_id` query parameter. If omitted, analytics run across all of the user's datasets.

#### GET `/api/analytics/kpis`

Key Performance Indicators — the business health snapshot.

**Query Parameters:** `dataset_id` (optional, integer)

**Response (200):**
```json
{
  "total_revenue": 2345678.90,
  "total_profit": 456789.12,
  "total_orders": 5200,
  "avg_order_value": 451.09,
  "overall_profit_margin": 19.47,
  "unique_customers": 793
}
```

**Business Context:** KPIs give managers an at-a-glance health check. Total revenue and profit show the top line, while profit margin reveals pricing effectiveness.

---

#### GET `/api/analytics/monthly-revenue`

Revenue and order count by month — identifies seasonal patterns.

**Response (200):**
```json
[
  {"period": "2023-01", "revenue": 189234.56, "order_count": 412},
  {"period": "2023-02", "revenue": 201456.78, "order_count": 438}
]
```

---

#### GET `/api/analytics/top-products`

Top products ranked by total revenue.

**Query Parameters:** `dataset_id`, `limit` (default: 10)

**Response (200):**
```json
[
  {
    "product_name": "Canon imageCLASS Printer",
    "category": "Technology",
    "total_revenue": 45678.90,
    "total_quantity": 234
  }
]
```

---

#### GET `/api/analytics/top-customers`

Top customers ranked by total spending.

**Query Parameters:** `dataset_id`, `limit` (default: 10)

**Response (200):**
```json
[
  {
    "customer_name": "Sean Miller",
    "segment": "Consumer",
    "total_revenue": 25678.90,
    "order_count": 42
  }
]
```

---

#### GET `/api/analytics/revenue-by-region`

Revenue, profit, and order count by geographic region.

**Response (200):**
```json
[
  {"region": "West", "revenue": 725000.00, "profit": 145000.00, "order_count": 1580},
  {"region": "East", "revenue": 680000.00, "profit": 130000.00, "order_count": 1420}
]
```

**Business Context:** Regional analysis helps allocate marketing budgets and identify underperforming territories.

---

#### GET `/api/analytics/revenue-by-state`

State-level revenue breakdown (top 15 by default).

**Response (200):**
```json
[
  {"state": "California", "region": "West", "revenue": 456789.00, "profit": 89123.00}
]
```

---

#### GET `/api/analytics/category-performance`

Performance metrics for each product category.

**Response (200):**
```json
[
  {
    "category": "Technology",
    "revenue": 836700.00,
    "profit": 145230.00,
    "profit_margin": 17.36,
    "order_count": 1847
  }
]
```

---

#### GET `/api/analytics/sales-trend`

Monthly revenue with month-over-month growth percentage.

**Response (200):**
```json
[
  {"period": "2023-01", "revenue": 189234.56, "growth_pct": null},
  {"period": "2023-02", "revenue": 201456.78, "growth_pct": 6.46}
]
```

---

#### GET `/api/analytics/customer-segments`

Revenue and behavior by customer segment.

**Response (200):**
```json
[
  {"segment": "Consumer", "revenue": 1100000.00, "customer_count": 410, "avg_order_value": 420.50}
]
```

---

#### GET `/api/analytics/subcategory-performance`

Revenue and profit at the sub-category level.

**Response (200):**
```json
[
  {"category": "Technology", "sub_category": "Phones", "revenue": 330000.00, "profit": 44000.00}
]
```

---

#### GET `/api/analytics/insights`

AI-generated business insights with actionable recommendations.

**Response (200):**
```json
[
  {
    "category": "Revenue",
    "title": "West Region Leads in Revenue",
    "description": "The West region generates 31% of total revenue, outperforming all other regions.",
    "metric": "$725,000",
    "recommendation": "Replicate West region strategies (product mix, pricing) in underperforming regions."
  }
]
```

---

### Forecast

#### POST `/api/forecast/train`

Train a Random Forest model on a dataset. **Protected.**

**Request Body:**
```json
{
  "dataset_id": 1
}
```

**Response (200):**
```json
{
  "id": 1,
  "dataset_id": 1,
  "model_type": "random_forest",
  "rmse": 156.78,
  "mae": 89.45,
  "r2_score": 0.82,
  "feature_importance": {
    "quantity": 0.23,
    "discount": 0.18,
    "category_Technology": 0.15,
    "order_month": 0.12
  },
  "predictions": [
    {"actual": 234.56, "predicted": 245.12},
    {"actual": 567.89, "predicted": 542.33}
  ],
  "created_at": "2024-01-15T10:30:00"
}
```

**Errors:**
- `400`: Dataset has fewer than 100 records (insufficient for training)

---

#### GET `/api/forecast/predict/{dataset_id}`

Get future sales predictions using a trained model. **Protected.**

**Query Parameters:** `periods` (default: 12, number of future months)

**Response (200):**
```json
[
  {"period": "2024-01", "predicted_sales": 198456.78},
  {"period": "2024-02", "predicted_sales": 205123.45}
]
```

**Errors:**
- `404`: No trained model found for this dataset

---

#### GET `/api/forecast/results/{dataset_id}`

Get the most recent training results for a dataset. **Protected.**

**Response:** Same shape as POST `/api/forecast/train` response.

---

### Reports

#### POST `/api/reports/generate`

Generate a business report. **Protected.**

**Request Body:**
```json
{
  "dataset_id": 1,
  "title": "Q4 2023 Sales Analysis",
  "report_type": "summary"
}
```

**Response (200):**
```json
{
  "id": 1,
  "title": "Q4 2023 Sales Analysis",
  "report_type": "summary",
  "created_at": "2024-01-15T10:30:00"
}
```

---

#### GET `/api/reports`

List all saved reports for the current user. **Protected.**

---

#### GET `/api/reports/{report_id}/download`

Download a report as CSV or PDF. **Protected.**

**Query Parameters:** `format` (default: "csv", options: "csv", "pdf")

**Response:** File download (Content-Type: text/csv or application/pdf)

---

#### DELETE `/api/reports/{report_id}`

Delete a saved report. **Protected.**

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

| Status Code | Meaning |
|------------|---------|
| 400 | Bad Request — invalid input or validation failure |
| 401 | Unauthorized — missing or invalid JWT token |
| 403 | Forbidden — valid token but insufficient permissions |
| 404 | Not Found — resource doesn't exist |
| 500 | Internal Server Error — unexpected server failure |
