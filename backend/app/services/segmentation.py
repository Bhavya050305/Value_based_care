from typing import Any, Dict

from app.ml.segmentation.predictor import SegmentationPredictor
from app.schemas.segmentation import SegmentationFeatures


class SegmentationService:
    """
    Service responsible for running the trained ACO segmentation model.

    The model itself is loaded by SegmentationPredictor.

    This service intentionally does NOT calculate or invent the 15
    model features. Those values must come from the backend/database.
    """

    def __init__(self):
        self.predictor = SegmentationPredictor()

    def predict(
        self,
        aco_id: str,
        performance_year: int,
        features: SegmentationFeatures,
    ) -> Dict[str, Any]:

        # Convert Pydantic model to dictionary
        feature_data = features.model_dump()

        # Run the trained segmentation pipeline
        prediction = self.predictor.predict(feature_data)

        return {
            "aco_id": aco_id,
            "performance_year": performance_year,
            "cluster": prediction["cluster"],
            "segment": prediction["segment"],
            "features": feature_data,
        }


segmentation_service = SegmentationService()