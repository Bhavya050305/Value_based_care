"""Admin API routes."""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_request_id, require_permissions
from app.core.security import AuthenticatedUser, Permission
from app.schemas.common import ApiResponse, ResponseMeta

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/status", response_model=ApiResponse[dict])
async def get_admin_status(
    user: AuthenticatedUser = Depends(require_permissions([Permission.MANAGE_SETTINGS])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[dict]:
    return ApiResponse(
        data={"admin_system": "active", "total_tenants": 1, "audit_status": "enabled"},
        meta=ResponseMeta(request_id=request_id),
    )
