"""Action Tracking API routes."""

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_request_id, require_permissions
from app.core.security import AuthenticatedUser, Permission
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.recommendations import (
    ActionCreateRequest,
    ActionUpdateRequest,
    ActionItem,
)
from app.services.recommendations import ActionService


router = APIRouter(
    prefix="/actions",
    tags=["Action Tracking"],
)

service = ActionService()


@router.get(
    "",
    response_model=ApiResponse[list[ActionItem]],
)
async def list_actions(
    aco_id: str | None = Query(
        None,
        description="Filter by ACO identifier",
    ),
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MANAGE_ACTIONS])
    ),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[list[ActionItem]]:
    """List actions for the user's organization."""

    data = await service.list_actions(
        aco_id,
        user.organization_id,
    )

    return ApiResponse(
        data=data,
        meta=ResponseMeta(request_id=request_id),
    )


@router.post(
    "",
    response_model=ApiResponse[ActionItem],
)
async def create_action(
    request_body: ActionCreateRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MANAGE_ACTIONS])
    ),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[ActionItem]:
    """Create a new action."""

    data = await service.create_action(
        request_body,
        user.organization_id,
    )

    return ApiResponse(
        data=data,
        meta=ResponseMeta(request_id=request_id),
    )


@router.get(
    "/{action_id}",
    response_model=ApiResponse[ActionItem],
)
async def get_action_by_id(
    action_id: str,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MANAGE_ACTIONS])
    ),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[ActionItem]:
    """Return one action by ID."""

    data = await service.get_action_by_id(
        action_id,
        user.organization_id,
    )

    return ApiResponse(
        data=data,
        meta=ResponseMeta(request_id=request_id),
    )


@router.patch(
    "/{action_id}",
    response_model=ApiResponse[ActionItem],
)
async def update_action(
    action_id: str,
    request_body: ActionUpdateRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MANAGE_ACTIONS])
    ),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[ActionItem]:
    """Update an existing action."""

    data = await service.update_action(
        action_id,
        request_body.model_dump(exclude_unset=True),
        user.organization_id,
    )

    return ApiResponse(
        data=data,
        meta=ResponseMeta(request_id=request_id),
    )


@router.post(
    "/{action_id}/complete",
    response_model=ApiResponse[ActionItem],
)
async def complete_action(
    action_id: str,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MANAGE_ACTIONS])
    ),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[ActionItem]:
    """Mark an action as completed."""

    data = await service.complete_action(
        action_id,
        user.organization_id,
    )

    return ApiResponse(
        data=data,
        meta=ResponseMeta(request_id=request_id),
    )