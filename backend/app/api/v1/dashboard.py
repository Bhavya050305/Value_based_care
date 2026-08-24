"""Dashboard API routes."""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import get_request_id, require_permissions
from app.core.security import AuthenticatedUser, Permission
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.portfolio import PortfolioSummaryData
from app.services.portfolio import PortfolioService

router = APIRouter(prefix="/dashboard", tags=["Dashboard Summary"])
service = PortfolioService()


@router.get("/summary", response_model=ApiResponse[PortfolioSummaryData])
async def get_dashboard_summary(
    year: int = Query(..., description="Performance year is required (2022, 2023, 2024)"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_PORTFOLIO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[PortfolioSummaryData]:
    """Retrieve aggregate performance metrics strictly for requested performance year."""
    data = await service.get_summary(db, year=year, organization_id=user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))
