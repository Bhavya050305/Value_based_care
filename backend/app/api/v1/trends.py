"""Historical Trends API routes."""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_request_id, require_permissions
from app.core.security import AuthenticatedUser, Permission
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.trends import HistoricalTrendData
from app.services.performance import TrendsService

router = APIRouter(prefix="/acos", tags=["Historical Trends"])
service = TrendsService()


@router.get("/{aco_id}/trends", response_model=ApiResponse[HistoricalTrendData])
async def get_historical_trends(
    aco_id: str,
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_ACO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[HistoricalTrendData]:
    data = await service.get_historical_trends(aco_id, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))
