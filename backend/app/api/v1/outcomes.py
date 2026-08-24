"""Outcomes API routes."""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_request_id, require_permissions
from app.core.security import AuthenticatedUser, Permission
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.recommendations import OutcomeCreateRequest, OutcomeImpact
from app.services.recommendations import OutcomeService

router = APIRouter(prefix="/actions", tags=["Action Outcomes"])
service = OutcomeService()


@router.get("/{action_id}/outcomes", response_model=ApiResponse[list[OutcomeImpact]])
async def get_action_outcomes(
    action_id: str,
    user: AuthenticatedUser = Depends(require_permissions([Permission.MANAGE_ACTIONS])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[list[OutcomeImpact]]:
    data = await service.get_outcomes_for_action(action_id, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.post("/{action_id}/outcomes", response_model=ApiResponse[OutcomeImpact])
async def create_action_outcome(
    action_id: str,
    request_body: OutcomeCreateRequest,
    user: AuthenticatedUser = Depends(require_permissions([Permission.MANAGE_ACTIONS])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[OutcomeImpact]:
    """Create and persist a real action outcome."""
    data = await service.create_outcome(action_id, request_body.model_dump(), user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/{action_id}/outcomes/{outcome_id}", response_model=ApiResponse[OutcomeImpact])
async def get_outcome_by_id(
    action_id: str,
    outcome_id: str,
    user: AuthenticatedUser = Depends(require_permissions([Permission.MANAGE_ACTIONS])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[OutcomeImpact]:
    """Return one outcome by ID."""
    data = await service.get_outcome_by_id(action_id, outcome_id, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))
