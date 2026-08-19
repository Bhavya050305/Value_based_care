"""Portfolio API routes."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import get_current_user, get_request_id, require_permissions
from app.core.security import AuthenticatedUser, Permission
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.portfolio import (
    PortfolioAcoItem,
    PortfolioOpportunity,
    PortfolioSummaryData,
    PortfolioTrendPoint,
    RiskDistributionItem,
)
from app.schemas.anomaly import AnomalyAlertsResponse
from app.services.portfolio import PortfolioService
from app.services.anomaly_service import AnomalyService

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])
service = PortfolioService()
anomaly_service = AnomalyService()


@router.get("/summary", response_model=ApiResponse[PortfolioSummaryData])
async def get_portfolio_summary(
    year: int = Query(..., description="Performance year is required (2022, 2023, 2024)"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_PORTFOLIO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[PortfolioSummaryData]:
    data = await service.get_summary(db, year, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/risk-distribution", response_model=ApiResponse[list[RiskDistributionItem]])
async def get_risk_distribution(
    year: int = Query(..., description="Performance year is required (2022, 2023, 2024)"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_PORTFOLIO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[list[RiskDistributionItem]]:
    data = await service.get_risk_distribution(db, year, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/trends", response_model=ApiResponse[list[PortfolioTrendPoint]])
async def get_portfolio_trends(
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_PORTFOLIO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[list[PortfolioTrendPoint]]:
    data = await service.get_portfolio_trends(db, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/acos", response_model=ApiResponse[list[PortfolioAcoItem]])
async def get_portfolio_acos(
    year: int = Query(..., description="Performance year is required (2022, 2023, 2024)"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_PORTFOLIO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[list[PortfolioAcoItem]]:
    data = await service.get_portfolio_acos(db, year, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/opportunities", response_model=ApiResponse[list[PortfolioOpportunity]])
async def get_opportunities(
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_PORTFOLIO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[list[PortfolioOpportunity]]:
    data = await service.get_opportunities(db, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/alerts", response_model=ApiResponse[AnomalyAlertsResponse])
async def get_alerts(
    year: int = Query(2024, description="Performance year (2022, 2023, 2024)"),
    category: Optional[str] = Query(None, description="Severity filter: ALL, HIGH, MEDIUM, LOW, NORMAL"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_PORTFOLIO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[AnomalyAlertsResponse]:
    data = await anomaly_service.get_all_alerts(db, year=year, category=category)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))
