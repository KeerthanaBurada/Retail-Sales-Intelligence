"""Dataset-related request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DatasetResponse(BaseModel):
    """Schema for returning dataset metadata."""
    id: int
    filename: str
    row_count: int
    column_count: int
    status: str
    upload_stats: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UploadResponse(BaseModel):
    """Schema for dataset upload results, including ETL stats."""
    dataset_id: int
    filename: str
    rows_processed: int
    rows_cleaned: int
    validation_errors: list[str]
    etl_stats: dict
