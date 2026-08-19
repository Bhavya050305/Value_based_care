"""Financial ML Model Service.

Loads best_GenSaveLoss_model.joblib pipeline and model_features.csv.
Provides real financial predictions using database records.
"""

from __future__ import annotations
import os
import joblib
import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.feature_builder import FeatureBuilder


class FinancialPredictionService:
    def __init__(self, artifacts_dir: Optional[str] = None):
        if not artifacts_dir:
            artifacts_dir = str(Path(__file__).resolve().parents[1] / "ml" / "artifacts")
        self.artifacts_dir = artifacts_dir
        self.model = None
        self.feature_names = []
        self._load_artifacts()

    def _load_artifacts(self):
        model_path = os.path.join(self.artifacts_dir, "best_GenSaveLoss_model.joblib")
        features_path = os.path.join(self.artifacts_dir, "model_features.csv")

        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
            except Exception as e:
                print(f"Warning: Failed to load financial ML model: {e}")

        if os.path.exists(features_path):
            try:
                df_feat = pd.read_csv(features_path)
                self.feature_names = df_feat["feature_name"].tolist()
            except Exception as e:
                print(f"Warning: Failed to load model features CSV: {e}")

    def is_loaded(self) -> bool:
        return self.model is not None and len(self.feature_names) > 0

    async def predict_for_aco(
        self, db: AsyncSession, aco_id: str, year: int
    ) -> Dict[str, Any]:
        """Query real database record for aco_id and year, build feature vector, and run ML model."""
        record = await FeatureBuilder.get_raw_financial_record(db, aco_id, year)
        if not record:
            return {
                "status": "RECORD_NOT_FOUND",
                "message": f"No financial record found for ACO {aco_id} in year {year}"
            }

        if not self.is_loaded():
            return {
                "status": "MODEL_UNAVAILABLE",
                "message": "Financial ML model artifact is not loaded"
            }

        # Build feature DataFrame
        X = FeatureBuilder.build_financial_model_features(record, self.feature_names)
        
        # Predict using full saved Pipeline (preprocessor + estimator)
        predicted_gensaveloss = float(self.model.predict(X)[0])

        mapping = record._mapping if hasattr(record, "_mapping") else record.__dict__
        actual_gensaveloss = mapping.get("GenSaveLoss")
        if actual_gensaveloss is None:
            actual_gensaveloss = mapping.get("target_GenSaveLoss", 0.0)

        abs_error = abs(predicted_gensaveloss - float(actual_gensaveloss)) if actual_gensaveloss is not None else None

        return {
            "status": "SUCCESS",
            "aco_id": aco_id,
            "performance_year": year,
            "predicted_gross_savings_loss": predicted_gensaveloss,
            "actual_gross_savings_loss": float(actual_gensaveloss) if actual_gensaveloss is not None else None,
            "absolute_error": abs_error,
            "model_version": "RandomForestRegressor_v1.0"
        }
