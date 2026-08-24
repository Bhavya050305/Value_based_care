"""Settings API routes."""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_request_id
from app.core.security import AuthenticatedUser
from app.schemas.assistant import (
    PreferencesUpdateRequest,
    ProfileSettings,
    ProfileUpdateRequest,
    UserPreferences,
)
from app.schemas.common import ApiResponse, ResponseMeta
from app.services.assistant import SettingsService

router = APIRouter(prefix="/settings", tags=["Settings"])
service = SettingsService()


@router.get("/profile", response_model=ApiResponse[ProfileSettings])
async def get_user_profile(
    user: AuthenticatedUser = Depends(get_current_user),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[ProfileSettings]:
    data = await service.get_profile(user.user_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.patch("/profile", response_model=ApiResponse[ProfileSettings])
async def update_user_profile(
    request_body: ProfileUpdateRequest,
    user: AuthenticatedUser = Depends(get_current_user),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[ProfileSettings]:
    """Update the authenticated user's profile."""
    data = await service.update_profile(user.user_id, request_body.model_dump(exclude_unset=True))
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/preferences", response_model=ApiResponse[UserPreferences])
async def get_user_preferences(
    user: AuthenticatedUser = Depends(get_current_user),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[UserPreferences]:
    data = await service.get_preferences(user.user_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.patch("/preferences", response_model=ApiResponse[UserPreferences])
async def update_user_preferences(
    request_body: PreferencesUpdateRequest,
    user: AuthenticatedUser = Depends(get_current_user),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[UserPreferences]:
    """Update the authenticated user's preferences."""
    data = await service.update_preferences(
        user.user_id, request_body.model_dump(exclude_unset=True)
    )
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))

