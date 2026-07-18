"""Analytics response schemas for dashboard and reporting endpoints."""

from typing import Optional

from pydantic import BaseModel


class RevenueByPeriod(BaseModel):
    """Revenue aggregated by time period (e.g., monthly, quarterly)."""
    period: str
    revenue: float
    order_count: int


class TopProduct(BaseModel):
    """Top-performing product by revenue."""
    product_name: str
    category: str
    total_revenue: float
    total_quantity: int


class TopCustomer(BaseModel):
    """Top customer by total spend."""
    customer_name: str
    segment: str
    total_revenue: float
    order_count: int


class RegionRevenue(BaseModel):
    """Revenue and profit breakdown by region."""
    region: str
    revenue: float
    profit: float
    order_count: int


class CategoryPerformance(BaseModel):
    """Performance metrics for a product category."""
    category: str
    revenue: float
    profit: float
    profit_margin: float
    order_count: int


class KPIMetrics(BaseModel):
    """High-level KPI summary for the dashboard."""
    total_revenue: float
    total_profit: float
    total_orders: int
    avg_order_value: float
    overall_profit_margin: float
    unique_customers: int


class StateRevenue(BaseModel):
    """Revenue and profit breakdown by state."""
    state: str
    region: str
    revenue: float
    profit: float


class SalesTrend(BaseModel):
    """Sales trend data point with optional growth percentage."""
    period: str
    revenue: float
    growth_pct: Optional[float] = None


class CustomerSegment(BaseModel):
    """Customer segment performance metrics."""
    segment: str
    revenue: float
    customer_count: int
    avg_order_value: float


class SubcategoryPerformance(BaseModel):
    """Performance metrics for a product sub-category."""
    category: str
    sub_category: str
    revenue: float
    profit: float


class BusinessInsight(BaseModel):
    """AI-generated business insight with actionable recommendation."""
    category: str
    title: str
    description: str
    metric: str
    recommendation: str
