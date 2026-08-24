from typing import Dict

from pydantic import BaseModel, Field


class SegmentationFeatures(BaseModel):
    SavingsLossPct: float
    ExpenditureVariancePct: float
    FinancialGap: float
    PMPM: float

    quality_score: float
    utilization_score: float

    ed_visits_per_beneficiary: float
    admissions_per_beneficiary: float
    advanced_imaging_per_beneficiary: float
    em_visit_intensity: float

    ed_utilization_change_yoy: float
    admission_change_yoy: float
    em_utilization_change_yoy: float
    advanced_imaging_change_yoy: float

    average_available_risk_score: float


class SegmentationRequest(BaseModel):
    aco_id: str = Field(..., min_length=1)
    performance_year: int
    features: SegmentationFeatures


class SegmentationResponse(BaseModel):
    aco_id: str
    performance_year: int
    cluster: int
    segment: str
    features: Dict[str, float]