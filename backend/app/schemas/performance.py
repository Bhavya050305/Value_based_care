"""ACO Performance domain schemas."""

from pydantic import BaseModel


class FinancialPerformance(BaseModel):
    """
    Precomputed financial performance for one ACO and one year.

    All values are retrieved from aco_financial_performance.
    """

    aco_id: str
    performance_year: int

    benchmark_expenditure: float | None = None
    actual_expenditure: float | None = None

    gross_savings_loss: float | None = None
    expenditure_variance: float | None = None
    expenditure_variance_pct: float | None = None

    pmpm: float | None = None
    benchmark_pmpm: float | None = None

    earned_shared_savings: float | None = None
    share_rate: float | None = None
    loss_rate: float | None = None

    total_actual_expenditure: float | None = None
    total_benchmark_expenditure: float | None = None


class QualityPerformance(BaseModel):
    aco_id: str
    performance_year: int
    quality_score: float | None = None
    measures: dict[str, float] | None = None


class UtilizationPerformance(BaseModel):
    aco_id: str
    performance_year: int
    inpatient_admissions_per_1k: float | None = None
    ed_visits_per_1k: float | None = None
    readmission_rate: float | None = None


class PerformanceSummary(BaseModel):
    aco_id: str
    aco_name: str
    performance_year: int
    financial: FinancialPerformance | None = None
    quality: QualityPerformance | None = None
    utilization: UtilizationPerformance | None = None