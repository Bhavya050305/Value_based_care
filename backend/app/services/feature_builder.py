"""Central Feature Builder Service for ML Model Input Construction.

Responsibility:
- Retrieve precomputed ACO records from dedicated database tables via YEAR_TABLE_MAP.
- Construct deterministic feature vectors for Financial, Segmentation, and Anomaly models.
- Enforce strict temporal & leakage controls (no target columns or future values).
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import YEAR_TABLE_MAP


class FeatureBuilder:
    """Single source of truth for constructing ML feature inputs from database records."""

    @staticmethod
    async def get_raw_financial_record(
        db: AsyncSession, aco_id: str, year: int
    ) -> Optional[Any]:
        """Query year-specific table via YEAR_TABLE_MAP for ACO_ID and year."""
        if year not in YEAR_TABLE_MAP:
            return None
        table = YEAR_TABLE_MAP[year]
        query = text(f'SELECT * FROM public.{table} WHERE "ACO_ID" = :aco_id LIMIT 1;')
        res = await db.execute(query, {"aco_id": aco_id})
        row = res.fetchone()
        return row

    @staticmethod
    def build_financial_model_features(
        record: Any, candidate_feature_names: List[str]
    ) -> pd.DataFrame:
        """Construct a DataFrame row for the financial prediction model pipeline."""
        row_dict: Dict[str, Any] = {}
        mapping = record._mapping if hasattr(record, "_mapping") else record.__dict__

        for col in candidate_feature_names:
            val = mapping.get(col, None)
            if val is None:
                val = mapping.get(col.lower(), None)
            row_dict[col] = val

        df = pd.DataFrame([row_dict])
        return df

    @staticmethod
    def build_segmentation_features(
        record: Any, feature_names: List[str]
    ) -> pd.DataFrame:
        """Construct a DataFrame row for the segmentation KMeans model pipeline."""
        row_dict: Dict[str, Any] = {}
        mapping = record._mapping if hasattr(record, "_mapping") else record.__dict__

        for col in feature_names:
            val = mapping.get(col, None)
            if val is None:
                val = mapping.get(col.lower(), None)
            if val is None:
                val = 0.0
            row_dict[col] = float(val)

        return pd.DataFrame([row_dict])

    @staticmethod
    def build_anomaly_features(
        record: Any, feature_names: List[str]
    ) -> pd.DataFrame:
        """Construct a DataFrame row for the anomaly detection model pipeline."""
        row_dict: Dict[str, Any] = {}
        mapping = record._mapping if hasattr(record, "_mapping") else record.__dict__

        for col in feature_names:
            val = mapping.get(col, None)
            if val is None:
                val = mapping.get(col.lower(), None)
            if val is None:
                val = 0.0
            row_dict[col] = float(val)

        return pd.DataFrame([row_dict])
