"""Health and readiness routes."""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from app.core.config import Settings
from app.core.dependencies import get_app_settings, get_request_id
from app.core.health import check_database, check_redis
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.health import HealthData, ReadinessChecks, ReadinessData

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=ApiResponse[HealthData])
async def health_check(
    settings: Settings = Depends(get_app_settings),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[HealthData]:
    return ApiResponse(
        data=HealthData(
            status="ok",
            version=settings.app_version,
            environment=settings.environment,
        ),
        meta=ResponseMeta(request_id=request_id),
    )


@router.get("/ready")
async def readiness_check(
    request: Request,
    request_id: str = Depends(get_request_id),
) -> JSONResponse:
    database = await check_database()
    redis = await check_redis()
    checks = ReadinessChecks(database=database, redis=redis)
    all_ready = database.available
    status_value = "ready" if all_ready else "not_ready"

    payload = ApiResponse(
        data=ReadinessData(status=status_value, checks=checks),
        meta=ResponseMeta(request_id=request_id),
    )
    http_status = status.HTTP_200_OK if all_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=http_status, content=payload.model_dump(mode="json"))


@router.get("/models")
async def model_health_check(
    request_id: str = Depends(get_request_id),
) -> JSONResponse:
    from app.services.financial_prediction import FinancialPredictionService
    from app.ml.segmentation.predictor import SegmentationPredictor
    from app.ml.anomaly.loader import model as anomaly_model

    fin_svc = FinancialPredictionService()
    seg_svc = SegmentationPredictor()

    models_status = {
        "financial_model": "loaded" if fin_svc.is_loaded() else "failed",
        "segmentation_model": "loaded" if hasattr(seg_svc, "model") and seg_svc.model is not None else "failed",
        "anomaly_model": "loaded" if anomaly_model is not None else "failed"
    }

    all_loaded = all(v == "loaded" for v in models_status.values())
    http_status = status.HTTP_200_OK if all_loaded else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=http_status,
        content={
            "status": "healthy" if all_loaded else "degraded",
            "models": models_status,
            "request_id": request_id
        }
    )

