from fastapi import APIRouter, HTTPException

from app.schemas.segmentation import (
    SegmentationRequest,
    SegmentationResponse,
)
from app.services.segmentation import segmentation_service


router = APIRouter(
    prefix="/segmentation",
    tags=["Segmentation"],
)


@router.post(
    "/predict",
    response_model=SegmentationResponse,
)
async def predict_segmentation(
    request: SegmentationRequest,
):
    """
    Predict the ACO performance segment using the trained
    KMeans segmentation model.
    """

    try:
        result = segmentation_service.predict(
            aco_id=request.aco_id,
            performance_year=request.performance_year,
            features=request.features,
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Segmentation prediction failed: {str(exc)}",
        )