"""ML prediction, forecasting, and explanation routes."""

from dataclasses import asdict, is_dataclass
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import get_request_id, require_permissions
from app.core.security import AuthenticatedUser, Permission
from app.schemas.common import ApiResponse, ResponseMeta
from app.services.ml_forecasting import MLForecastingService
from app.services.drivers import DriversService

router = APIRouter(
    prefix="/predictions",
    tags=["ML Predictions & Explanations"],
)

ml_service = MLForecastingService()
drivers_service = DriversService()


@router.get(
    "/forecast/{aco_id}",
    response_model=ApiResponse[dict],
)
async def get_3year_financial_forecast(
    aco_id: str,
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.READ_PREDICTIONS])
    ),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[dict]:
    """Generate 3-year financial trend forecast (2025-2027) for an ACO based on 2022-2024 baseline."""
    data = await ml_service.get_aco_3year_forecast(db, aco_id=aco_id)
    return ApiResponse(
        data=data,
        meta=ResponseMeta(request_id=request_id),
    )


@router.get(
    "/{aco_id}",
    response_model=ApiResponse[dict],
)
async def get_prediction(
    aco_id: str,
    target_year: int = Query(2025, description="Target year for ML forecasting"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.READ_PREDICTIONS])
    ),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[dict]:
    """Generate ML predictions and multi-model evaluation metrics for an ACO."""
    data = await ml_service.get_aco_forecast(db, aco_id=aco_id, target_year=target_year)
    return ApiResponse(
        data=data,
        meta=ResponseMeta(request_id=request_id),
    )



@router.get(
    "/{prediction_id}/explanation",
    response_model=ApiResponse[dict],
)
async def get_prediction_explanation(
    prediction_id: str,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.READ_PREDICTIONS])
    ),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[dict]:

    data = await drivers_service.get_prediction_explanation(
        prediction_id,
        user.organization_id,
    )
    if is_dataclass(data):
        data_dict = asdict(data)
    elif hasattr(data, "model_dump"):
        data_dict = data.model_dump()
    elif isinstance(data, dict):
        data_dict = data
    else:
        data_dict = dict(data)

    return ApiResponse(
        data=data_dict,
        meta=ResponseMeta(request_id=request_id),
    )