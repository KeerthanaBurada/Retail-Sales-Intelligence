"""
Analytics Service - SQL-powered business intelligence queries.

Each method answers a specific business question by querying the sales_records
table. All queries use SQLAlchemy text() with bound parameters to prevent
SQL injection. Results are returned as plain dicts ready for JSON serialization.
"""

from sqlalchemy import text
from sqlalchemy.orm import Session


def _dataset_filter(dataset_id: int | None) -> str:
    """Append a dataset_id WHERE clause when filtering by a specific upload."""
    if dataset_id:
        return "AND dataset_id = :dataset_id"
    return ""


def _params(dataset_id: int | None, **extra) -> dict:
    """Build the parameter dict, including dataset_id only when provided."""
    params = {}
    if dataset_id:
        params["dataset_id"] = dataset_id
    params.update(extra)
    return params


class AnalyticsService:
    """Static methods for each analytics query the dashboard needs."""

    @staticmethod
    def get_kpi_metrics(db: Session, dataset_id: int | None = None) -> dict:
        """
        High-level KPIs — gives managers a quick health check of the business.

        Returns total orders, revenue, profit, unique customers, average order
        value, and overall profit margin.
        """
        query = text(f"""
            SELECT
                COUNT(DISTINCT order_id) AS total_orders,
                SUM(sales)              AS total_revenue,
                SUM(profit)             AS total_profit,
                COUNT(DISTINCT customer_name) AS unique_customers
            FROM sales_records
            WHERE 1=1 {_dataset_filter(dataset_id)}
        """)

        row = db.execute(query, _params(dataset_id)).fetchone()

        if row is None or row.total_orders == 0:
            return {
                "total_orders": 0,
                "total_revenue": 0.0,
                "total_profit": 0.0,
                "unique_customers": 0,
                "avg_order_value": 0.0,
                "profit_margin": 0.0,
            }

        total_orders = row.total_orders or 0
        total_revenue = float(row.total_revenue or 0)
        total_profit = float(row.total_profit or 0)
        unique_customers = row.unique_customers or 0

        avg_order_value = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0
        profit_margin = round(total_profit / total_revenue * 100, 2) if total_revenue > 0 else 0.0

        return {
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "total_profit": round(total_profit, 2),
            "unique_customers": unique_customers,
            "avg_order_value": avg_order_value,
            "profit_margin": profit_margin,
        }

    @staticmethod
    def get_monthly_revenue(db: Session, dataset_id: int | None = None) -> list[dict]:
        """
        Monthly revenue trend — helps identify seasonality and growth patterns.

        Returns a chronologically ordered list of {period, revenue, order_count}.
        """
        query = text(f"""
            SELECT
                order_year,
                order_month,
                SUM(sales) AS revenue,
                COUNT(DISTINCT order_id) AS order_count
            FROM sales_records
            WHERE 1=1 {_dataset_filter(dataset_id)}
            GROUP BY order_year, order_month
            ORDER BY order_year, order_month
        """)

        rows = db.execute(query, _params(dataset_id)).fetchall()

        return [
            {
                "period": f"{row.order_year}-{row.order_month:02d}",
                "revenue": round(float(row.revenue or 0), 2),
                "order_count": row.order_count or 0,
            }
            for row in rows
        ]

    @staticmethod
    def get_top_products(db: Session, dataset_id: int | None = None, limit: int = 10) -> list[dict]:
        """
        Top products by revenue — identifies best sellers for inventory planning.
        """
        query = text(f"""
            SELECT
                product_name,
                category,
                SUM(sales)    AS total_revenue,
                SUM(quantity) AS total_quantity
            FROM sales_records
            WHERE 1=1 {_dataset_filter(dataset_id)}
            GROUP BY product_name, category
            ORDER BY total_revenue DESC
            LIMIT :limit
        """)

        rows = db.execute(query, _params(dataset_id, limit=limit)).fetchall()

        return [
            {
                "product_name": row.product_name,
                "category": row.category,
                "total_revenue": round(float(row.total_revenue or 0), 2),
                "total_quantity": int(row.total_quantity or 0),
            }
            for row in rows
        ]

    @staticmethod
    def get_top_customers(db: Session, dataset_id: int | None = None, limit: int = 10) -> list[dict]:
        """
        Top customers by revenue — supports key-account management strategy.
        """
        query = text(f"""
            SELECT
                customer_name,
                segment,
                SUM(sales) AS total_revenue,
                COUNT(DISTINCT order_id) AS order_count
            FROM sales_records
            WHERE 1=1 {_dataset_filter(dataset_id)}
            GROUP BY customer_name, segment
            ORDER BY total_revenue DESC
            LIMIT :limit
        """)

        rows = db.execute(query, _params(dataset_id, limit=limit)).fetchall()

        return [
            {
                "customer_name": row.customer_name,
                "segment": row.segment,
                "total_revenue": round(float(row.total_revenue or 0), 2),
                "order_count": row.order_count or 0,
            }
            for row in rows
        ]

    @staticmethod
    def get_revenue_by_region(db: Session, dataset_id: int | None = None) -> list[dict]:
        """
        Revenue breakdown by region — shows geographic performance distribution.
        """
        query = text(f"""
            SELECT
                region,
                SUM(sales)  AS revenue,
                SUM(profit) AS profit,
                COUNT(DISTINCT order_id) AS order_count
            FROM sales_records
            WHERE 1=1 {_dataset_filter(dataset_id)}
            GROUP BY region
        """)

        rows = db.execute(query, _params(dataset_id)).fetchall()

        return [
            {
                "region": row.region,
                "revenue": round(float(row.revenue or 0), 2),
                "profit": round(float(row.profit or 0), 2),
                "order_count": row.order_count or 0,
            }
            for row in rows
        ]

    @staticmethod
    def get_revenue_by_state(db: Session, dataset_id: int | None = None, limit: int = 15) -> list[dict]:
        """
        Top states by revenue — enables state-level sales strategy.
        """
        query = text(f"""
            SELECT
                state,
                region,
                SUM(sales)  AS revenue,
                SUM(profit) AS profit
            FROM sales_records
            WHERE 1=1 {_dataset_filter(dataset_id)}
            GROUP BY state, region
            ORDER BY revenue DESC
            LIMIT :limit
        """)

        rows = db.execute(query, _params(dataset_id, limit=limit)).fetchall()

        return [
            {
                "state": row.state,
                "region": row.region,
                "revenue": round(float(row.revenue or 0), 2),
                "profit": round(float(row.profit or 0), 2),
            }
            for row in rows
        ]

    @staticmethod
    def get_category_performance(db: Session, dataset_id: int | None = None) -> list[dict]:
        """
        Category-level P&L — answers 'which product categories are most profitable?'
        Profit margin is computed in Python to keep the SQL portable across DBs.
        """
        query = text(f"""
            SELECT
                category,
                SUM(sales)  AS revenue,
                SUM(profit) AS profit,
                COUNT(DISTINCT order_id) AS order_count
            FROM sales_records
            WHERE 1=1 {_dataset_filter(dataset_id)}
            GROUP BY category
        """)

        rows = db.execute(query, _params(dataset_id)).fetchall()

        results = []
        for row in rows:
            revenue = float(row.revenue or 0)
            profit = float(row.profit or 0)
            profit_margin = round(profit / revenue * 100, 2) if revenue > 0 else 0.0

            results.append({
                "category": row.category,
                "revenue": round(revenue, 2),
                "profit": round(profit, 2),
                "order_count": row.order_count or 0,
                "profit_margin": profit_margin,
            })

        return results

    @staticmethod
    def get_sales_trend(db: Session, dataset_id: int | None = None) -> list[dict]:
        """
        Monthly sales trend with month-over-month growth percentage.

        Growth % shows acceleration/deceleration — a key metric for investors
        and leadership. First month has growth_pct = None (no prior baseline).
        """
        monthly_data = AnalyticsService.get_monthly_revenue(db, dataset_id)

        results = []
        for i, month in enumerate(monthly_data):
            if i == 0:
                growth_pct = None
            else:
                prev_revenue = monthly_data[i - 1]["revenue"]
                if prev_revenue > 0:
                    growth_pct = round(
                        (month["revenue"] - prev_revenue) / prev_revenue * 100, 2
                    )
                else:
                    growth_pct = None

            results.append({
                "period": month["period"],
                "revenue": month["revenue"],
                "order_count": month["order_count"],
                "growth_pct": growth_pct,
            })

        return results

    @staticmethod
    def get_customer_segments(db: Session, dataset_id: int | None = None) -> list[dict]:
        """
        Segment analysis — compares Consumer vs Corporate vs Home Office
        buying behaviour (revenue, customer count, avg order value).
        """
        query = text(f"""
            SELECT
                segment,
                SUM(sales) AS revenue,
                COUNT(DISTINCT customer_name) AS customer_count,
                COUNT(DISTINCT order_id) AS order_count
            FROM sales_records
            WHERE 1=1 {_dataset_filter(dataset_id)}
            GROUP BY segment
        """)

        rows = db.execute(query, _params(dataset_id)).fetchall()

        results = []
        for row in rows:
            revenue = float(row.revenue or 0)
            order_count = row.order_count or 0
            avg_order_value = round(revenue / order_count, 2) if order_count > 0 else 0.0

            results.append({
                "segment": row.segment,
                "revenue": round(revenue, 2),
                "customer_count": row.customer_count or 0,
                "avg_order_value": avg_order_value,
            })

        return results

    @staticmethod
    def get_subcategory_performance(db: Session, dataset_id: int | None = None) -> list[dict]:
        """
        Sub-category drill-down — answers 'within each category, what sells best?'
        Useful for merchandising and assortment decisions.
        """
        query = text(f"""
            SELECT
                category,
                sub_category,
                SUM(sales)  AS revenue,
                SUM(profit) AS profit
            FROM sales_records
            WHERE 1=1 {_dataset_filter(dataset_id)}
            GROUP BY category, sub_category
            ORDER BY revenue DESC
        """)

        rows = db.execute(query, _params(dataset_id)).fetchall()

        return [
            {
                "category": row.category,
                "sub_category": row.sub_category,
                "revenue": round(float(row.revenue or 0), 2),
                "profit": round(float(row.profit or 0), 2),
            }
            for row in rows
        ]
