"""What-If Simulator API routes."""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_request_id, require_permissions
from app.core.security import AuthenticatedUser, Permission
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.simulator import SimulationRequest, SimulationResult
from app.services.simulator import SimulatorService

router = APIRouter(prefix="/simulations", tags=["What-If Simulator"])
aco_simulations_router = APIRouter(prefix="/acos", tags=["What-If Simulator"])
service = SimulatorService()


@router.post("", response_model=ApiResponse[SimulationResult])
async def run_simulation(
    request_body: SimulationRequest,
    user: AuthenticatedUser = Depends(require_permissions([Permission.EXECUTE_SIMULATION])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[SimulationResult]:
    data = await service.run_simulation(request_body, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/{simulation_id}", response_model=ApiResponse[SimulationResult])
async def get_simulation_by_id(
    simulation_id: str,
    user: AuthenticatedUser = Depends(require_permissions([Permission.EXECUTE_SIMULATION])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[SimulationResult]:
    """Return stored simulation result."""
    data = await service.get_simulation_by_id(simulation_id, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@aco_simulations_router.get("/{aco_id}/simulations", response_model=ApiResponse[list[SimulationResult]])
async def list_aco_simulations(
    aco_id: str,
    user: AuthenticatedUser = Depends(require_permissions([Permission.EXECUTE_SIMULATION])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[list[SimulationResult]]:
    """Return previous simulations for the selected ACO."""
    data = await service.list_simulations_for_aco(aco_id, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))

