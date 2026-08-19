"""Performance Drivers and Predictions API routes."""

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_user, get_request_id, require_permissions
from app.core.security import AuthenticatedUser, Permission
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.drivers import DriverExplanations, PredictionResult
from app.services.drivers import DriversService

router = APIRouter(prefix="/acos", tags=["Performance Drivers"])
service = DriversService()


@router.get("/{aco_id}/drivers", response_model=ApiResponse[DriverExplanations])
async def get_aco_drivers(
    aco_id: str,
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_PREDICTIONS])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[DriverExplanations]:
    data = await service.get_drivers(aco_id, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/{aco_id}/predictions", response_model=ApiResponse[PredictionResult])
async def get_aco_predictions(
    aco_id: str,
    year: int = Query(2024, description="Target prediction year"),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_PREDICTIONS])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[PredictionResult]:
    data = await service.get_predictions(aco_id, year, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))
