"""ACO Performance API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import get_current_user, get_request_id, require_permissions
from app.core.security import AuthenticatedUser, Permission
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.performance import (
    FinancialPerformance,
    PerformanceSummary,
    QualityPerformance,
    UtilizationPerformance,
)
from app.services.performance import PerformanceService

router = APIRouter(prefix="/acos", tags=["ACO Performance"])
service = PerformanceService()


@router.get("/{aco_id}/summary", response_model=ApiResponse[PerformanceSummary])
async def get_performance_summary(
    aco_id: str,
    year: int = Query(..., description="Performance year is required (2022, 2023, 2024)"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_ACO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[PerformanceSummary]:
    data = await service.get_summary(aco_id, year, user.organization_id, db=db)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/{aco_id}/financial", response_model=ApiResponse[FinancialPerformance])
async def get_financial_performance(
    aco_id: str,
    year: int = Query(..., description="Performance year is required (2022, 2023, 2024)"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_ACO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[FinancialPerformance]:
    data = await service.get_financial(aco_id, year, user.organization_id, db=db)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/{aco_id}/quality", response_model=ApiResponse[QualityPerformance])
async def get_quality_performance(
    aco_id: str,
    year: int = Query(..., description="Performance year is required (2022, 2023, 2024)"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_ACO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[QualityPerformance]:
    data = await service.get_quality(aco_id, year, user.organization_id, db=db)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/{aco_id}/utilization", response_model=ApiResponse[UtilizationPerformance])
async def get_utilization_performance(
    aco_id: str,
    year: int = Query(..., description="Performance year is required (2022, 2023, 2024)"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_ACO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[UtilizationPerformance]:
    data = await service.get_utilization(aco_id, year, user.organization_id, db=db)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/{aco_id}/providers", response_model=ApiResponse[list[dict]])
async def get_aco_providers(
    aco_id: str,
    year: int = Query(2024, description="Performance year"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_ACO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[list[dict]]:
    """Retrieve clinician panel variation data for a specific ACO."""
    data = await service.get_providers(aco_id, year, user.organization_id, db=db)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))
