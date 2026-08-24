"""Production ML inference for ACO GenSaveLoss prediction."""

from pathlib import Path
import warnings

import joblib
import pandas as pd


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[3]

ARTIFACT_DIR = BASE_DIR / "app" / "ml" / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "best_GenSaveLoss_model.joblib"
METADATA_PATH = ARTIFACT_DIR / "model_metadata.joblib"
FEATURES_PATH = ARTIFACT_DIR / "model_features.csv"


# ------------------------------------------------------------
# LOAD MODEL ARTIFACTS (WITH GRACEFUL FALLBACK)
# ------------------------------------------------------------

MODEL = None
METADATA = None
FEATURES = None
EXPECTED_FEATURES = None
MODEL_LOAD_ERROR = None

def load_model_artifacts():
    """Lazy load model artifacts with error handling."""
    global MODEL, METADATA, FEATURES, EXPECTED_FEATURES, MODEL_LOAD_ERROR
    
    try:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"ML model artifact not found: {MODEL_PATH}")
        
        if not METADATA_PATH.exists():
            raise FileNotFoundError(f"Model metadata not found: {METADATA_PATH}")
        
        if not FEATURES_PATH.exists():
            raise FileNotFoundError(f"Model feature file not found: {FEATURES_PATH}")
        
        # Try loading with warning suppression for version mismatches
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            MODEL = joblib.load(MODEL_PATH)
            METADATA = joblib.load(METADATA_PATH)
            FEATURES = pd.read_csv(FEATURES_PATH)
        
        # Validate
        EXPECTED_FEATURES = FEATURES["feature_name"].tolist()
        EXPECTED_FEATURE_COUNT = METADATA["number_of_features"]
        
        if len(EXPECTED_FEATURES) != EXPECTED_FEATURE_COUNT:
            raise ValueError(
                "Model feature count mismatch: "
                f"metadata={EXPECTED_FEATURE_COUNT}, "
                f"features_file={len(EXPECTED_FEATURES)}"
            )
        
        print("ML model artifacts loaded successfully")
        
    except Exception as e:
        MODEL_LOAD_ERROR = str(e)
        print(f"Warning: Could not load ML model artifacts: {e}")
        print("  Predictions will not be available until model is fixed or retrained")


# Attempt to load on import
load_model_artifacts()


# ------------------------------------------------------------
# PREDICTOR
# ------------------------------------------------------------

class GenSaveLossPredictor:
    """Runs inference using the trained GenSaveLoss model."""

    def __init__(self):
        if MODEL is None:
            raise RuntimeError(
                f"ML model not available: {MODEL_LOAD_ERROR}. "
                "Model needs to be fixed, retrained, or scikit-learn version needs adjustment."
            )
        self.model = MODEL
        self.metadata = METADATA
        self.feature_names = EXPECTED_FEATURES if FEATURES is not None else []

    def validate_features(self, data: dict) -> None:
        """Validate that all required model features are present."""
        
        if not self.feature_names:
            raise RuntimeError("Model features not loaded")

        missing_features = [
            feature
            for feature in self.feature_names
            if feature not in data
        ]

        if missing_features:
            raise ValueError(
                "Missing required ML features: "
                + ", ".join(missing_features)
            )

    def predict(self, data: dict) -> float:
        """
        Generate GenSaveLoss prediction.

        Parameters
        ----------
        data:
            Dictionary containing the 61 model features.

        Returns
        -------
        float
            Predicted target_GenSaveLoss.
        """
        
        if self.model is None:
            raise RuntimeError("ML model not loaded. Cannot make predictions.")

        self.validate_features(data)

        # Keep only the exact training features and exact order.
        input_df = pd.DataFrame(
            [
                {
                    feature: data[feature]
                    for feature in self.feature_names
                }
            ]
        )

        prediction = self.model.predict(input_df)

        return float(prediction[0])


# ------------------------------------------------------------
# SINGLETON (LAZY INITIALIZATION)
# ------------------------------------------------------------

predictor = None

def get_predictor():
    """Get or create the predictor instance."""
    global predictor
    if predictor is None:
        if MODEL is None:
            raise RuntimeError(
                f"ML model not available: {MODEL_LOAD_ERROR}. "
                "Predictions cannot be made until the model is fixed or retrained."
            )
        predictor = GenSaveLossPredictor()
    return predictor


# Try to instantiate on import, but don't fail if model is unavailable
try:
    predictor = GenSaveLossPredictor()
except RuntimeError as e:
    print(f"ℹ Predictor will be available after model is loaded: {e}")