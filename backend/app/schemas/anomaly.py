from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class AnomalyResponse(BaseModel):
    aco_id: str
    performance_year: int
    is_anomaly: bool
    prediction: int
    decision_score: float
    score_sample: float
    features: Dict[str, float]


class AnomalyAlertItem(BaseModel):
    id: str
    aco_id: str
    aco_name: str
    performance_year: int
    severity: str  # "HIGH", "MEDIUM", "LOW", "NORMAL"
    status: str = "active"
    is_anomaly: bool
    score: float
    metric: str
    explanation: str
    recommended_action: str
    savings_loss: float
    features: Dict[str, float]


class AnomalyAlertsCounts(BaseModel):
    total: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    normal: int = 0


class AnomalyAlertsResponse(BaseModel):
    performance_year: int
    total_acos: int
    counts: AnomalyAlertsCounts
    alerts: List[AnomalyAlertItem]