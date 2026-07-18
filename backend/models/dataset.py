from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255))
    row_count = Column(Integer)
    column_count = Column(Integer)
    status = Column(String(50), default="processed")
    upload_stats = Column(Text, nullable=True)  # JSON string of ETL stats
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="datasets")
    sales_records = relationship(
        "SalesRecord", back_populates="dataset", cascade="all, delete-orphan"
    )
    forecast_results = relationship("ForecastResult", back_populates="dataset")


class SalesRecord(Base):
    __tablename__ = "sales_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False, index=True)
    order_id = Column(String(50))
    order_date = Column(Date)
    ship_date = Column(Date, nullable=True)
    ship_mode = Column(String(50), nullable=True)
    customer_id = Column(String(50), nullable=True)
    customer_name = Column(String(255))
    segment = Column(String(50))
    city = Column(String(100))
    state = Column(String(100))
    region = Column(String(50))
    category = Column(String(50))
    sub_category = Column(String(50))
    product_name = Column(String(500))
    sales = Column(Float)
    quantity = Column(Integer)
    discount = Column(Float)
    profit = Column(Float)

    # Derived/engineered columns
    order_month = Column(Integer, nullable=True)
    order_year = Column(Integer, nullable=True)
    order_day_of_week = Column(Integer, nullable=True)
    profit_margin = Column(Float, nullable=True)
    processing_days = Column(Integer, nullable=True)

    # Relationship
    dataset = relationship("Dataset", back_populates="sales_records")
