"""Unit tests for ML anomaly detection predictor and service features."""

from app.ml.anomaly.predictor import predict_anomaly
from app.services.anomaly_service import AnomalyService


def test_predict_anomaly_normal_sample():
    sample_features = {
        "ed_utilization_change_yoy": 0.01,
        "admission_change_yoy": -0.02,
        "em_utilization_change_yoy": 0.05,
        "advanced_imaging_change_yoy": 0.00,
        "readmission_proxy_rate_yoy_change": -0.01,
        "savings_yoy_change_pct": 2.5,
        "expenditure_variance_pct": -1.2,
        "quality_change_yoy": 1.0,
        "provider_utilization_variation": 0.05,
        "provider_cost_variation": 0.03,
    }

    result = predict_anomaly(sample_features)

    assert "is_anomaly" in result
    assert "decision_score" in result
    assert "prediction" in result
    assert isinstance(result["is_anomaly"], bool)
    assert isinstance(result["decision_score"], float)


def test_anomaly_service_required_features():
    service = AnomalyService()
    assert len(service.REQUIRED_FEATURES) == 10
    assert "ed_utilization_change_yoy" in service.REQUIRED_FEATURES
    assert "provider_cost_variation" in service.REQUIRED_FEATURES
