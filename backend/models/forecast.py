from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class ForecastResult(Base):
    __tablename__ = "forecast_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    model_type = Column(String(50), default="random_forest")
    rmse = Column(Float)
    mae = Column(Float)
    r2_score = Column(Float)
    feature_importance = Column(Text)  # JSON string
    predictions = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="forecast_results")
    dataset = relationship("Dataset", back_populates="forecast_results")


class SavedReport(Base):
    __tablename__ = "saved_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255))
    report_type = Column(String(50))
    report_data = Column(Text)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="saved_reports")
