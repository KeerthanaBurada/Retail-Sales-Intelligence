import os
import json
import uuid
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from config import UPLOAD_DIR
from models.user import User
from models.dataset import Dataset, SalesRecord
from schemas.dataset import DatasetResponse, UploadResponse
from services.etl_service import ETLService
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix='/api/datasets', tags=['Datasets'])


@router.post('/upload', response_model=UploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a CSV file, run ETL, and store cleaned records."""
    # Save uploaded file to disk with a unique name
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    contents = await file.read()
    with open(file_path, 'wb') as f:
        f.write(contents)

    # Run ETL pipeline
    result = ETLService.process_upload(file_path)

    if result['validation_errors']:
        raise HTTPException(400, detail={'errors': result['validation_errors']})

    cleaned_df = result['cleaned_df']

    # Create dataset metadata entry
    dataset = Dataset(
        user_id=current_user.id,
        filename=file.filename,
        row_count=len(cleaned_df),
        column_count=len(cleaned_df.columns),
        status='processed',
        upload_stats=json.dumps(result['stats'])
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    # Bulk insert cleaned records into SalesRecord table
    records = []
    for row in cleaned_df.itertuples(index=False):
        order_date_val = getattr(row, 'Order Date', None) if hasattr(row, 'Order Date') else getattr(row, '_6', None)
        ship_date_val = getattr(row, 'Ship Date', None) if hasattr(row, 'Ship Date') else getattr(row, '_7', None)

        # Helper to safely get attribute by column name (handles spaces via _asdict fallback)
        row_dict = row._asdict() if hasattr(row, '_asdict') else {}

        def get_val(col_name, default=None):
            """Get value from row, converting NaN to None."""
            val = row_dict.get(col_name, default)
            if val is not None and pd.isna(val):
                return default
            return val

        # Convert date fields - handle both datetime and date objects
        order_date = get_val('Order Date')
        if hasattr(order_date, 'date'):
            order_date = order_date.date()

        ship_date = get_val('Ship Date')
        if hasattr(ship_date, 'date'):
            ship_date = ship_date.date()

        sales_val = get_val('Sales', 0.0)
        quantity_val = get_val('Quantity', 0)
        discount_val = get_val('Discount', 0.0)
        profit_val = get_val('Profit', 0.0)

        record = SalesRecord(
            dataset_id=dataset.id,
            order_id=get_val('Order ID'),
            order_date=order_date,
            ship_date=ship_date,
            ship_mode=get_val('Ship Mode'),
            customer_id=get_val('Customer ID'),
            customer_name=get_val('Customer Name'),
            segment=get_val('Segment'),
            city=get_val('City'),
            state=get_val('State'),
            region=get_val('Region'),
            category=get_val('Category'),
            sub_category=get_val('Sub-Category'),
            product_name=get_val('Product Name'),
            sales=float(sales_val) if pd.notna(sales_val) else 0.0,
            quantity=int(quantity_val) if pd.notna(quantity_val) else 0,
            discount=float(discount_val) if pd.notna(discount_val) else 0.0,
            profit=float(profit_val) if pd.notna(profit_val) else 0.0,
            order_month=get_val('order_month'),
            order_year=get_val('order_year'),
            order_day_of_week=get_val('order_day_of_week'),
            profit_margin=float(get_val('profit_margin', 0.0)) if pd.notna(get_val('profit_margin', 0.0)) else 0.0,
            processing_days=int(get_val('processing_days', 0)) if pd.notna(get_val('processing_days', 0)) else 0
        )
        records.append(record)

    db.bulk_save_objects(records)
    db.commit()

    return UploadResponse(
        dataset_id=dataset.id,
        filename=file.filename,
        rows_processed=result['original_rows'],
        rows_cleaned=len(cleaned_df),
        validation_errors=[],
        etl_stats=result['stats']
    )


@router.get('/', response_model=list[DatasetResponse])
def list_datasets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all datasets belonging to the current user."""
    datasets = (
        db.query(Dataset)
        .filter(Dataset.user_id == current_user.id)
        .order_by(Dataset.created_at.desc())
        .all()
    )
    return [DatasetResponse.model_validate(d) for d in datasets]


@router.get('/{dataset_id}', response_model=DatasetResponse)
def get_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific dataset by ID."""
    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id, Dataset.user_id == current_user.id)
        .first()
    )
    if not dataset:
        raise HTTPException(404, detail='Dataset not found')
    return DatasetResponse.model_validate(dataset)


@router.delete('/{dataset_id}')
def delete_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a dataset and its associated records."""
    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id, Dataset.user_id == current_user.id)
        .first()
    )
    if not dataset:
        raise HTTPException(404, detail='Dataset not found')

    db.delete(dataset)
    db.commit()
    return {'message': 'Dataset deleted successfully'}
