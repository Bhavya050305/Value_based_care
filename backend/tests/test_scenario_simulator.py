"""Unit tests for what-if scenario simulator engine."""

import pytest
from app.schemas.simulator import SimulationRequest
from app.services.simulator import SimulatorService


@pytest.mark.asyncio
async def test_simulator_service_run_and_retrieve():
    service = SimulatorService()

    request = SimulationRequest(
        aco_id="A1001",
        target_year=2025,
        quality_score_delta=2.0,
        utilization_change_pct=-3.0,
    )

    result = await service.run_simulation(request)

    assert result.simulation_id.startswith("sim_")
    assert result.aco_id == "A1001"
    assert result.expenditure_impact.delta_value < 0
    assert result.savings_impact.delta_value > 0

    fetched = await service.get_simulation_by_id(result.simulation_id)
    assert fetched.simulation_id == result.simulation_id

    acos_sims = await service.list_simulations_for_aco("A1001")
    assert len(acos_sims) == 1
