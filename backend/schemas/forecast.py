"""Forecast request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ForecastRequest(BaseModel):
    """Schema for requesting a forecast on a dataset."""
    dataset_id: int


class PredictionPoint(BaseModel):
    """A single actual vs. predicted data point."""
    actual: float
    predicted: float


class ForecastResponse(BaseModel):
    """Schema for returning forecast results and model metrics."""
    id: int
    dataset_id: int
    model_type: str
    rmse: float
    mae: float
    r2_score: float
    feature_importance: dict
    predictions: list
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FuturePrediction(BaseModel):
    """A single future period prediction."""
    period: str
    predicted_sales: float
