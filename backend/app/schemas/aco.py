"""ACO Explorer domain schemas."""

from pydantic import BaseModel


class AcoDetail(BaseModel):
    id: str
    aco_id: str
    name: str
    performance_year: int | None = 2024
    state: str | None = None
    track: str | None = None
    agreement_type: str | None = None
    risk_model: str | None = None
    risk_level: str | None = "LOW"
    attributed_members: int | None = 0
    benchmark_expenditure: float | None = 0.0
    actual_expenditure: float | None = 0.0
    savings_loss: float | None = 0.0
    earned_shared_savings: float | None = 0.0
    savings_loss_pct: float | None = 0.0
    pmpm: float | None = 0.0
    benchmark_pmpm: float | None = 0.0
    quality_score: float | None = 0.0
    created_at: str | None = None



class AcoListItem(BaseModel):
    id: str
    aco_id: str
    name: str
    state: str | None = None
    track: str | None = None
    agreement_type: str | None = None
    risk_level: str | None = "LOW"
    attributed_members: int | None = 0
    benchmark_pmpm: float | None = 0.0
    pmpm: float | None = 0.0
    savings_loss: float | None = 0.0
    savings_loss_pct: float | None = 0.0
    quality_score: float | None = 0.0
