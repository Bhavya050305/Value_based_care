"""Performance Drivers and Predictions domain schemas."""

from pydantic import BaseModel


class FeatureImportance(BaseModel):
    feature_name: str
    shap_value: float
    feature_value: float | None = None
    impact: str  # positive | negative | neutral


class DriverExplanations(BaseModel):
    aco_id: str
    prediction_id: str | None = None
    top_drivers: list[FeatureImportance]
    summary_explanation: str


class PredictionResult(BaseModel):
    prediction_id: str
    aco_id: str
    performance_year: int
    model_name: str
    model_version: str
    predicted_savings: float | None = None
    risk_score: float | None = None
    available: bool = True