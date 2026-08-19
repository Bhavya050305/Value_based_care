"""What-If Simulation engine service."""

import uuid
from app.schemas.simulator import MetricDelta, SimulationRequest, SimulationResult


class SimulatorService:
    """Calculates scenario deltas based on baseline metrics and parameter shifts."""

    def __init__(self) -> None:
        self._simulations: dict[str, SimulationResult] = {}

    async def run_simulation(
        self, request: SimulationRequest, organization_id: str | None = None
    ) -> SimulationResult:
        baseline_exp = 125000000.0
        baseline_savings = 4200000.0

        util_factor = 1.0 + ((request.utilization_change_pct or 0.0) / 100.0)
        quality_impact = (request.quality_score_delta or 0.0) * 150000.0

        simulated_exp = baseline_exp * util_factor
        simulated_savings = (baseline_exp - simulated_exp) + baseline_savings + quality_impact

        exp_delta = simulated_exp - baseline_exp
        savings_delta = simulated_savings - baseline_savings

        sim_id = f"sim_{uuid.uuid4().hex[:8]}"
        result = SimulationResult(
            simulation_id=sim_id,
            aco_id=request.aco_id,
            model_version="SimEngine_v1.0",
            expenditure_impact=MetricDelta(
                baseline_value=baseline_exp,
                simulated_value=simulated_exp,
                delta_value=exp_delta,
                percentage_change=(exp_delta / baseline_exp) * 100.0 if baseline_exp else 0.0,
            ),
            savings_impact=MetricDelta(
                baseline_value=baseline_savings,
                simulated_value=simulated_savings,
                delta_value=savings_delta,
                percentage_change=(savings_delta / baseline_savings) * 100.0 if baseline_savings else 0.0,
            ),
            limitations=[
                "Estimates are model-assisted projections based on historical MSSP data.",
                "External macroeconomic shifts or regional healthcare policy changes are not modeled.",
            ],
        )
        self._simulations[sim_id] = result
        return result

    async def get_simulation_by_id(
        self, simulation_id: str, organization_id: str | None = None
    ) -> SimulationResult:
        if simulation_id in self._simulations:
            return self._simulations[simulation_id]
        from app.core.exceptions import AppError, ErrorCode

        raise AppError(
            code=ErrorCode.NOT_FOUND,
            message=f"Simulation '{simulation_id}' was not found.",
            status_code=404,
        )

    async def list_simulations_for_aco(
        self, aco_id: str, organization_id: str | None = None
    ) -> list[SimulationResult]:
        return [sim for sim in self._simulations.values() if sim.aco_id == aco_id]

