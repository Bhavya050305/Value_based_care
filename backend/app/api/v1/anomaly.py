from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.services.anomaly_service import AnomalyService
from app.schemas.anomaly import AnomalyAlertsResponse, AnomalyResponse
from app.schemas.common import ApiResponse, ResponseMeta


router = APIRouter(
    prefix="/acos",
    tags=["Anomaly Detection"],
)


@router.get(
    "/alerts",
    response_model=ApiResponse[AnomalyAlertsResponse],
)
async def get_anomaly_alerts(
    year: int = Query(2024, description="Performance year (2022, 2023, 2024)"),
    category: Optional[str] = Query(None, description="Severity category filter: ALL, HIGH, MEDIUM, LOW, NORMAL"),
    db: AsyncSession = Depends(get_db_session),
):
    service = AnomalyService()
    data = await service.get_all_alerts(db=db, year=year, category=category)
    return ApiResponse(data=data)


@router.get(
    "/{aco_id}/anomaly",
    response_model=AnomalyResponse,
)
async def detect_anomaly(
    aco_id: str,
    year: int = Query(2024, description="Performance year"),
    db: AsyncSession = Depends(get_db_session),
):
    service = AnomalyService()
    return await service.detect(
        aco_id=aco_id,
        year=year,
        db=db,
    )