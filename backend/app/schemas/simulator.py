"""What-If Simulator domain schemas."""

from pydantic import BaseModel


class SimulationRequest(BaseModel):
    aco_id: str
    target_year: int
    quality_score_delta: float | None = 0.0
    utilization_change_pct: float | None = 0.0
    beneficiary_count_delta: int | None = 0


class MetricDelta(BaseModel):
    baseline_value: float
    simulated_value: float
    delta_value: float
    percentage_change: float


class SimulationResult(BaseModel):
    simulation_id: str
    aco_id: str
    model_version: str
    expenditure_impact: MetricDelta
    savings_impact: MetricDelta
    limitations: list[str]
