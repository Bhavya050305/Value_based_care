from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import require_permissions
from app.core.security import AuthenticatedUser, Permission
from app.schemas.peer_target import (
    PeerTargetRequest,
    PeerTargetResponse,
)
from app.services.peer_target import (
    peer_target_service
)

router = APIRouter(
    prefix="/peer-target",
    tags=["Peer Target"]
)


@router.post(
    "/find-peers",
    response_model=PeerTargetResponse
)
@router.post(
    "/find-peer-targets",
    response_model=PeerTargetResponse
)
async def find_peer_targets_post(
    request: PeerTargetRequest,
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_ACO])),
):
    try:
        return await peer_target_service.get_peer_targets(
            aco_id=request.aco_id,
            performance_year=request.get_year(),
            limit=request.limit,
            offset=request.offset,
            db=db,
            features=request.features,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


@router.get(
    "/find-peers",
    response_model=PeerTargetResponse
)
async def find_peer_targets_get(
    aco_id: str = Query(..., description="Target ACO ID"),
    performance_year: int = Query(2024, description="Performance year (2022, 2023, 2024)"),
    limit: int = Query(20, ge=1, le=100, description="Page limit"),
    offset: int = Query(0, ge=0, description="Page offset"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_ACO])),
):
    try:
        return await peer_target_service.get_peer_targets(
            aco_id=aco_id,
            performance_year=performance_year,
            limit=limit,
            offset=offset,
            db=db,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


@router.post(
    "/predict",
    response_model=PeerTargetResponse
)
async def predict_peer_target(
    request: PeerTargetRequest,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        return await peer_target_service.get_peer_targets(
            aco_id=request.aco_id,
            performance_year=request.get_year(),
            limit=request.limit,
            offset=request.offset,
            db=db,
            features=request.features,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )