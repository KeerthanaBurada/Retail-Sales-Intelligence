import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.forecast import ForecastResult
from schemas.forecast import ForecastRequest, ForecastResponse
from services.ml_service import MLService
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix='/api/forecast', tags=['Forecast'])


@router.post('/train', response_model=ForecastResponse)
def train_model(
    request: ForecastRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Train a forecasting model on the specified dataset."""
    result = MLService.train_model(db, request.dataset_id, current_user.id)
    return result


@router.get('/predict/{dataset_id}')
def predict_future(
    dataset_id: int,
    periods: int = Query(12, ge=1, le=36),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate future revenue predictions for the given dataset."""
    predictions = MLService.predict_future(db, dataset_id, periods)
    return predictions


@router.get('/results/{dataset_id}')
def get_forecast_results(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve the latest forecast results for a dataset."""
    result = (
        db.query(ForecastResult)
        .filter(ForecastResult.dataset_id == dataset_id)
        .order_by(ForecastResult.created_at.desc())
        .first()
    )
    if not result:
        raise HTTPException(404, detail='No forecast results found for this dataset')

    feature_importance = json.loads(result.feature_importance)
    predictions = json.loads(result.predictions)

    return {
        'id': result.id,
        'dataset_id': result.dataset_id,
        'model_type': result.model_type,
        'rmse': result.rmse,
        'mae': result.mae,
        'r2_score': result.r2_score,
        'feature_importance': feature_importance,
        'predictions': predictions,
        'created_at': result.created_at
    }
