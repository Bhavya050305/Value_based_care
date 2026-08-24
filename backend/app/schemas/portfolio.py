"""Portfolio domain schemas."""

from pydantic import BaseModel
from app.schemas.common import DataAvailability


class PortfolioSummaryData(BaseModel):
    performance_year: int = 2024
    total_acos: int = 0
    total_beneficiaries: int = 0
    total_benchmark_expenditure: float = 0.0
    total_actual_expenditure: float = 0.0
    net_savings_loss: float = 0.0
    earned_shared_savings: float = 0.0
    average_quality_score: float = 0.0
    good_standing: int = 0
    needs_attention: int = 0
    at_risk: int = 0


class RiskDistributionItem(BaseModel):
    risk_level: str
    count: int
    percentage: float


class PortfolioTrendPoint(BaseModel):
    performance_year: int
    gross_savings_loss: float
    earned_shared_savings: float
    average_quality_score: float
    actual_expenditure: float = 0.0
    benchmark_expenditure: float = 0.0


class PortfolioAcoItem(BaseModel):
    id: str
    aco_id: str
    name: str
    state: str | None = None
    track: str | None = None
    agreement_type: str | None = None
    savings_loss: float | None = None
    quality_score: float | None = None


class PortfolioOpportunity(BaseModel):
    id: str
    aco_id: str
    aco_name: str
    opportunity_type: str
    potential_savings: float
    description: str


class PortfolioAlert(BaseModel):
    id: str
    aco_id: str
    aco_name: str
    severity: str
    message: str
    created_at: str
