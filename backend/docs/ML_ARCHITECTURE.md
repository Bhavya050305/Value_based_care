# ML Architecture

## Status

**Awaiting ML team YAML configuration and model artifacts.**

## Separation of Concerns

| Component | Location | Runs When |
|-----------|----------|-----------|
| Training | `app/ml/training/`, `scripts/train_models.py` | Offline / CI job |
| Inference | `app/ml/inference/` | API request (via service layer) |
| Features | `app/ml/features/` | Inference + training |
| Explainability | `app/ml/explainability/` | After inference (SHAP) |
| Artifacts | `app/ml/artifacts/` | Loaded at startup or on demand |

Training must **never** run inside API request handlers.

## Inference Flow

```
API Request
    ↓
PredictionService
    ↓
FeatureBuilder (YAML-driven feature list)
    ↓
ModelRegistry (load XGBoost/LightGBM artifact)
    ↓
Prediction + confidence
    ↓
SHAP Explainer
    ↓
Persist prediction + explanation (never overwrite history)
    ↓
Response with model_name, model_version, feature_version, predicted_at
```

## Model Versioning

Every prediction record retains:

- `model_name`
- `model_version`
- `feature_version`
- `prediction_timestamp`
- `prediction_value`
- `confidence` (when supported)

Historical predictions are append-only.

## Unavailable States

| Condition | Response Status |
|-----------|-----------------|
| Artifact missing | `MODEL_UNAVAILABLE` |
| YAML missing/invalid | `MODEL_UNAVAILABLE` |
| Required features missing | `INSUFFICIENT_FEATURES` with `missing_features` list |

Never return fabricated probabilities or SHAP values.

## Integration Steps (Phase 12–13)

1. Receive YAML config(s) per model task.
2. Validate YAML schema (features, preprocessing, target, model type).
3. Load and verify artifact compatibility.
4. Implement `ModelRegistry` and `FeatureBuilder`.
5. Wire `PredictionService` and `ExplanationService`.
6. Map outputs to supplied database tables.
7. Update this document with model task → endpoint mapping.

## Required Inputs

- [ ] YAML model configuration(s)
- [ ] Trained model artifacts (XGBoost/LightGBM)
- [ ] Feature definitions and preprocessing specs
- [ ] Target variable definitions per model
- [ ] Approved model tasks (risk, savings, quality, etc.)
- [ ] Database tables for predictions and explanations
