from app.ml.segmentation.predictor import SegmentationPredictor


predictor = SegmentationPredictor()

test_features = {
    "SavingsLossPct": 0.0,
    "ExpenditureVariancePct": 0.0,
    "FinancialGap": 0.0,
    "PMPM": 0.0,
    "quality_score": 0.0,
    "utilization_score": 0.0,
    "ed_visits_per_beneficiary": 0.0,
    "admissions_per_beneficiary": 0.0,
    "advanced_imaging_per_beneficiary": 0.0,
    "em_visit_intensity": 0.0,
    "ed_utilization_change_yoy": 0.0,
    "admission_change_yoy": 0.0,
    "em_utilization_change_yoy": 0.0,
    "advanced_imaging_change_yoy": 0.0,
    "average_available_risk_score": 0.0,
}

result = predictor.predict(test_features)

print("=" * 80)
print("SEGMENTATION PREDICTION TEST")
print("=" * 80)
print(result)