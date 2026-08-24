"""Member Attribution & Risk API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import get_request_id, require_permissions
from app.core.security import AuthenticatedUser, Permission
from app.schemas.common import ApiResponse, ResponseMeta
from app.services.member import MemberService

router = APIRouter(prefix="", tags=["Member Attribution"])
service = MemberService()


@router.get("/members/risk", response_model=ApiResponse[dict])
async def get_member_risk(
    acoId: str = Query("A1001", description="ACO ID"),
    year: int = Query(2024, description="Performance year"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_ACO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[dict]:
    """Get population risk profile and member attribution list for a specific ACO."""
    data = await service.get_member_risk(db, aco_id=acoId, year=year)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/acos/{aco_id}/members", response_model=ApiResponse[dict])
async def get_aco_members(
    aco_id: str,
    year: int = Query(2024, description="Performance year"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_ACO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[dict]:
    """Get beneficiary attribution records for a specific ACO."""
    data = await service.get_member_risk(db, aco_id=aco_id, year=year)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))
