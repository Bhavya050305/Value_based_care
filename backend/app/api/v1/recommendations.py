"""Recommendations API routes."""

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_user, get_request_id, require_permissions
from app.core.security import AuthenticatedUser, Permission
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.recommendations import RecommendationItem
from app.services.recommendations import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])
service = RecommendationService()


@router.get("", response_model=ApiResponse[list[RecommendationItem]])
async def list_recommendations(
    aco_id: str | None = Query(None, description="Filter by ACO identifier"),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_PORTFOLIO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[list[RecommendationItem]]:
    data = await service.list_recommendations(aco_id, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/{recommendation_id}", response_model=ApiResponse[RecommendationItem])
async def get_recommendation(
    recommendation_id: str,
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_PORTFOLIO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[RecommendationItem]:
    data = await service.get_recommendation_by_id(recommendation_id, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.post("/{recommendation_id}/accept", response_model=ApiResponse[RecommendationItem])
async def accept_recommendation(
    recommendation_id: str,
    user: AuthenticatedUser = Depends(require_permissions([Permission.MANAGE_RECOMMENDATIONS])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[RecommendationItem]:
    data = await service.accept_recommendation(recommendation_id, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.post("/{recommendation_id}/dismiss", response_model=ApiResponse[RecommendationItem])
async def dismiss_recommendation(
    recommendation_id: str,
    user: AuthenticatedUser = Depends(require_permissions([Permission.MANAGE_RECOMMENDATIONS])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[RecommendationItem]:
    data = await service.dismiss_recommendation(recommendation_id, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))
