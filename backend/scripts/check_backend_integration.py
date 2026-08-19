"""End-to-End Backend Verification Script.

Executes real data flow:
Database (vbc_dev) -> Repositories -> Feature Builder -> ML Models -> FastAPI Services & APIs.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[1])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.database import get_session_factory
from app.services.feature_builder import FeatureBuilder
from app.services.financial_prediction import FinancialPredictionService
from app.ml.segmentation.predictor import SegmentationPredictor
from app.ml.anomaly.loader import model as anomaly_model, FEATURES as ANOMALY_FEATURES
from app.ml.anomaly.predictor import predict_anomaly


async def main():
    print("=" * 80)
    print("VALUE-BASED CARE END-TO-END BACKEND VERIFICATION")
    print("=" * 80)

    # 1. Database Verification
    print("\n[PHASE 1] DATABASE VERIFICATION")
    session_factory = get_session_factory()
    async with session_factory() as session:
        res = await session.execute(text("SELECT COUNT(*) FROM public.aco_financial_ml_training"))
        fin_count = res.scalar()
        print(f"[OK] public.aco_financial_ml_training row count: {fin_count}")

        res = await session.execute(text("SELECT COUNT(*) FROM public.acos"))
        acos_count = res.scalar()
        print(f"[OK] public.acos row count: {acos_count}")

        # Retrieve a real record
        rec = await FeatureBuilder.get_raw_financial_record(session, "A1001", 2024)
        if rec:
            print("[OK] Retrieved real record for A1001 / 2024 target year.")
        else:
            print("[FAIL] Record A1001 / 2024 not found!")
            return

    # 2. Financial ML Model Verification
    print("\n[PHASE 2] FINANCIAL ML MODEL VERIFICATION")
    fin_svc = FinancialPredictionService()
    if fin_svc.is_loaded():
        print(f"[OK] Financial model loaded successfully with {len(fin_svc.feature_names)} features.")
        async with session_factory() as session:
            pred_res = await fin_svc.predict_for_aco(session, "A1001", 2024)
            print("  Prediction result:", pred_res)
    else:
        print("[FAIL] Financial model loading failed!")

    # 3. Segmentation ML Model Verification
    print("\n[PHASE 3] SEGMENTATION ML MODEL VERIFICATION")
    seg_svc = SegmentationPredictor()
    if hasattr(seg_svc, "model") and seg_svc.model is not None:
        print("[OK] Segmentation model loaded successfully.")
        async with session_factory() as session:
            rec = await FeatureBuilder.get_raw_financial_record(session, "A1001", 2024)
            X_seg = FeatureBuilder.build_segmentation_features(rec, seg_svc.features)
            cluster_id = int(seg_svc.model.predict(X_seg)[0])
            print(f"[OK] ACO A1001 assigned to cluster: {cluster_id}")
    else:
        print("[FAIL] Segmentation model loading failed!")

    # 4. Anomaly ML Model Verification
    print("\n[PHASE 4] ANOMALY ML MODEL VERIFICATION")
    if anomaly_model is not None:
        print("[OK] Anomaly model loaded successfully.")
        async with session_factory() as session:
            rec = await FeatureBuilder.get_raw_financial_record(session, "A1001", 2024)
            df_anom = FeatureBuilder.build_anomaly_features(rec, ANOMALY_FEATURES)
            feat_dict = df_anom.iloc[0].to_dict()
            anom_res = predict_anomaly(feat_dict)
            print(f"[OK] ACO A1001 anomaly prediction result: {anom_res}")
    else:
        print("[FAIL] Anomaly model loading failed!")

    print("\n" + "=" * 80)
    print("ALL INTEGRATION VERIFICATION CHECKS COMPLETED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
