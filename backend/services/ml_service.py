"""Sales Forecasting using Random Forest Regressor.

Why Random Forest over alternatives:
- Linear Regression assumes linear relationships, but retail sales have complex
  non-linear patterns (seasonal spikes, promotional effects, category interactions).
- LSTM (deep learning) requires large sequential datasets and extensive tuning,
  which is overkill for tabular retail data with ~5000 rows.
- Random Forest handles non-linear relationships naturally, works well with
  mixed feature types (categorical + numerical), and provides feature importance
  rankings that help explain which factors drive sales.
- It's also robust to outliers and doesn't require feature scaling.
"""

import json
import os
import numpy as np
import pandas as pd
import joblib
from math import sqrt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from fastapi import HTTPException
from sqlalchemy.orm import Session

from config import MODEL_DIR
from models.dataset import SalesRecord
from models.forecast import ForecastResult


class MLService:

    @staticmethod
    def prepare_features(records) -> tuple:
        """Convert SalesRecord objects into feature matrix + target vector.

        Extracts temporal, numeric, and categorical features, applies one-hot
        encoding, and handles missing values.
        """
        data = []
        for r in records:
            data.append({
                'order_month': r.order_month,
                'order_year': r.order_year,
                'order_day_of_week': r.order_day_of_week,
                'quantity': r.quantity,
                'discount': r.discount,
                'processing_days': r.processing_days,
                'segment': r.segment,
                'region': r.region,
                'category': r.category,
                'sales': r.sales,
            })

        df = pd.DataFrame(data)

        # Fill missing processing_days with median so the model doesn't choke
        df['processing_days'] = df['processing_days'].fillna(df['processing_days'].median())

        # Target variable
        y = df['sales'].values

        # One-hot encode categorical columns
        df = pd.get_dummies(df, columns=['segment', 'region', 'category'])

        # Drop the target from features
        X = df.drop(columns=['sales'])
        feature_names = list(X.columns)

        return X.values, y, feature_names

    @staticmethod
    def train_model(db: Session, dataset_id: int, user_id: int) -> dict:
        """Train a Random Forest model on the given dataset and persist results."""
        records = (
            db.query(SalesRecord)
            .filter(SalesRecord.dataset_id == dataset_id)
            .all()
        )

        if len(records) < 100:
            raise HTTPException(
                status_code=400,
                detail='Need at least 100 records to train a model'
            )

        X, y, feature_names = MLService.prepare_features(records)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        # Evaluation metrics
        rmse = sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        # Top 10 most important features
        importance_pairs = sorted(
            zip(feature_names, model.feature_importances_),
            key=lambda x: x[1],
            reverse=True,
        )[:10]
        feature_importance = {name: round(float(imp), 4) for name, imp in importance_pairs}

        # Sample predictions for visual comparison (first 50 test samples)
        predictions = [
            {'actual': round(float(a), 2), 'predicted': round(float(p), 2)}
            for a, p in zip(y_test[:50], y_pred[:50])
        ]

        # Persist the trained model and its feature layout
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(model, f"{MODEL_DIR}/{dataset_id}_model.joblib")
        joblib.dump(feature_names, f"{MODEL_DIR}/{dataset_id}_features.joblib")

        # Save results to the database
        result = ForecastResult(
            dataset_id=dataset_id,
            user_id=user_id,
            model_type='random_forest',
            rmse=round(rmse, 4),
            mae=round(mae, 4),
            r2_score=round(r2, 4),
            feature_importance=json.dumps(feature_importance),
            predictions=json.dumps(predictions),
        )
        db.add(result)
        db.commit()
        db.refresh(result)

        return {
            'id': result.id,
            'dataset_id': result.dataset_id,
            'model_type': result.model_type,
            'rmse': result.rmse,
            'mae': result.mae,
            'r2_score': result.r2_score,
            'feature_importance': feature_importance,
            'predictions': predictions,
            'created_at': result.created_at.isoformat() if result.created_at else None,
        }

    @staticmethod
    def predict_future(db: Session, dataset_id: int, periods: int = 12) -> list[dict]:
        """Generate future sales predictions using a previously trained model."""
        model_path = f"{MODEL_DIR}/{dataset_id}_model.joblib"
        features_path = f"{MODEL_DIR}/{dataset_id}_features.joblib"

        if not os.path.exists(model_path):
            raise HTTPException(
                status_code=404,
                detail='No trained model found. Train a model first.'
            )

        model = joblib.load(model_path)
        feature_names = joblib.load(features_path)

        # Pull historical records to derive baseline feature values
        records = (
            db.query(SalesRecord)
            .filter(SalesRecord.dataset_id == dataset_id)
            .all()
        )

        data = []
        for r in records:
            data.append({
                'order_month': r.order_month,
                'order_year': r.order_year,
                'order_day_of_week': r.order_day_of_week,
                'quantity': r.quantity,
                'discount': r.discount,
                'processing_days': r.processing_days,
                'segment': r.segment,
                'region': r.region,
                'category': r.category,
            })

        df = pd.DataFrame(data)

        # Baseline numeric values from the historical data
        avg_quantity = df['quantity'].mean()
        avg_discount = df['discount'].mean()
        median_processing = df['processing_days'].median()

        # Most common categorical values (used as defaults for future rows)
        mode_segment = df['segment'].mode().iloc[0]
        mode_region = df['region'].mode().iloc[0]
        mode_category = df['category'].mode().iloc[0]

        # Determine the starting point for future months
        last_year = int(df['order_year'].max())
        last_month = int(df.loc[df['order_year'] == last_year, 'order_month'].max())

        forecasts = []
        current_year = last_year
        current_month = last_month

        for _ in range(periods):
            # Advance one month, rolling over the year boundary
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

            # Build a single-row DataFrame matching the training schema
            row = {
                'order_month': current_month,
                'order_year': current_year,
                'order_day_of_week': 2,  # Wednesday as a neutral default
                'quantity': avg_quantity,
                'discount': avg_discount,
                'processing_days': median_processing,
                'segment': mode_segment,
                'region': mode_region,
                'category': mode_category,
            }
            row_df = pd.DataFrame([row])
            row_df = pd.get_dummies(row_df, columns=['segment', 'region', 'category'])

            # Align columns to match the trained feature set exactly
            for col in feature_names:
                if col not in row_df.columns:
                    row_df[col] = 0
            row_df = row_df[feature_names]

            pred = model.predict(row_df.values)[0]
            forecasts.append({
                'period': f'{current_year}-{current_month:02d}',
                'predicted_sales': round(float(pred), 2),
            })

        return forecasts
