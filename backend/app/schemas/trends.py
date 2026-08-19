"""Historical Trends domain schemas."""

from pydantic import BaseModel
from app.schemas.performance import FinancialPerformance, QualityPerformance, UtilizationPerformance


class HistoricalTrendData(BaseModel):
    aco_id: str
    years: list[int]
    financial_trends: list[FinancialPerformance]
    quality_trends: list[QualityPerformance]
    utilization_trends: list[UtilizationPerformance]
