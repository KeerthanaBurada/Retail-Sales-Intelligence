from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from middleware.auth_middleware import get_current_user
from services.analytics_service import AnalyticsService
from services.insights_service import InsightsService

router = APIRouter(prefix='/api/analytics', tags=['Analytics'])


@router.get('/kpis')
def get_kpis(
    dataset_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get key performance indicator metrics."""
    return AnalyticsService.get_kpi_metrics(db, dataset_id)


@router.get('/monthly-revenue')
def get_monthly_revenue(
    dataset_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly revenue data for trend charts."""
    return AnalyticsService.get_monthly_revenue(db, dataset_id)


@router.get('/top-products')
def get_top_products(
    limit: int = Query(10),
    dataset_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get top-selling products by revenue."""
    return AnalyticsService.get_top_products(db, dataset_id, limit)


@router.get('/top-customers')
def get_top_customers(
    limit: int = Query(10),
    dataset_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get top customers by total spending."""
    return AnalyticsService.get_top_customers(db, dataset_id, limit)


@router.get('/revenue-by-region')
def get_revenue_by_region(
    dataset_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get revenue breakdown by geographic region."""
    return AnalyticsService.get_revenue_by_region(db, dataset_id)


@router.get('/revenue-by-state')
def get_revenue_by_state(
    limit: int = Query(15),
    dataset_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get top states by revenue."""
    return AnalyticsService.get_revenue_by_state(db, dataset_id, limit)


@router.get('/category-performance')
def get_category_performance(
    dataset_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance metrics broken down by product category."""
    return AnalyticsService.get_category_performance(db, dataset_id)


@router.get('/sales-trend')
def get_sales_trend(
    dataset_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily/weekly sales trend data."""
    return AnalyticsService.get_sales_trend(db, dataset_id)


@router.get('/customer-segments')
def get_customer_segments(
    dataset_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get revenue and order data by customer segment."""
    return AnalyticsService.get_customer_segments(db, dataset_id)


@router.get('/subcategory-performance')
def get_subcategory_performance(
    dataset_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance metrics for product sub-categories."""
    return AnalyticsService.get_subcategory_performance(db, dataset_id)


@router.get('/insights')
def get_insights(
    dataset_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI-driven business insights from sales data."""
    return InsightsService.generate_insights(db, dataset_id)
