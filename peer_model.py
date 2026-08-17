import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ============================================================
# FEATURES USED BY THE PEER TARGET FINDER
# ============================================================

NUMERIC_FEATURES = [
    "log_N_AB",
    "log_PMPM",

    "CMS_HCC_RiskScore_ESRD_PY",
    "CMS_HCC_RiskScore_DIS_PY",
    "CMS_HCC_RiskScore_AGDU_PY",
    "CMS_HCC_RiskScore_AGND_PY",

    "Pct_Age_0_64",
    "Pct_Age_65_74",
    "Pct_Age_75_84",
    "Pct_Age_85plus",

    "Pct_Female",
    "Pct_White",
    "Pct_Black",
    "Pct_Race_Other",
    "Perc_Dual",

    "ED_Visits_per_Ben",
    "EM_Visits_per_Ben",
    "SNF_Adm_per_Ben",

    "PCP_per_1000",
    "Spec_per_1000",
    "Hosp_per_1000",
]

CATEGORICAL_FEATURES = [
    "Agree_Type",
    "Risk_Model",
    "Rev_Exp_Cat",
]


# ============================================================
# FEATURE ENGINEERING
# ============================================================

class PeerFeatureEngineer(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X):

        X = X.copy()

        # -----------------------------
        # Basic numeric values
        # -----------------------------

        n_ab = pd.to_numeric(
            X["N_AB"],
            errors="coerce"
        )

        total_exp = pd.to_numeric(
            X["ABtotExp"],
            errors="coerce"
        )

        # PMPM
        pmpm = total_exp / n_ab / 12.0

        result = pd.DataFrame(index=X.index)

        # -----------------------------
        # Log transformed size/cost
        # -----------------------------

        result["log_N_AB"] = np.log1p(
            n_ab.clip(lower=0)
        )

        result["log_PMPM"] = np.log1p(
            pmpm.clip(lower=0)
        )

        # -----------------------------
        # Risk features
        # -----------------------------

        risk_columns = [
            "CMS_HCC_RiskScore_ESRD_PY",
            "CMS_HCC_RiskScore_DIS_PY",
            "CMS_HCC_RiskScore_AGDU_PY",
            "CMS_HCC_RiskScore_AGND_PY",
        ]

        for column in risk_columns:
            result[column] = pd.to_numeric(
                X[column],
                errors="coerce"
            )

        # -----------------------------
        # Age / gender / race percentages
        # -----------------------------

        percentage_features = [
            ("N_Ben_Age_0_64", "Pct_Age_0_64"),
            ("N_Ben_Age_65_74", "Pct_Age_65_74"),
            ("N_Ben_Age_75_84", "Pct_Age_75_84"),
            ("N_Ben_Age_85plus", "Pct_Age_85plus"),
            ("N_Ben_Female", "Pct_Female"),
            ("N_Ben_Race_White", "Pct_White"),
            ("N_Ben_Race_Black", "Pct_Black"),
            ("N_Ben_Race_Other", "Pct_Race_Other"),
        ]

        for source_column, new_column in percentage_features:

            value = pd.to_numeric(
                X[source_column],
                errors="coerce"
            )

            result[new_column] = (
                value / n_ab * 100.0
            )

        # Already a percentage
        result["Perc_Dual"] = pd.to_numeric(
            X["Perc_Dual"],
            errors="coerce"
        )

        # -----------------------------
        # Utilization per beneficiary
        # -----------------------------

        utilization_features = [
            ("P_EDV_Vis", "ED_Visits_per_Ben"),
            ("P_EM_Total", "EM_Visits_per_Ben"),
            ("P_SNF_ADM", "SNF_Adm_per_Ben"),
        ]

        for source_column, new_column in utilization_features:

            value = pd.to_numeric(
                X[source_column],
                errors="coerce"
            )

            result[new_column] = value / n_ab

        # -----------------------------
        # Provider density per 1000
        # -----------------------------

        provider_features = [
            ("N_PCP", "PCP_per_1000"),
            ("N_Spec", "Spec_per_1000"),
            ("N_Hosp", "Hosp_per_1000"),
        ]

        for source_column, new_column in provider_features:

            value = pd.to_numeric(
                X[source_column],
                errors="coerce"
            )

            result[new_column] = (
                value / n_ab * 1000.0
            )

        # -----------------------------
        # Categorical values
        # -----------------------------

        result["Agree_Type"] = (
            X["Agree_Type"]
            .astype("string")
            .str.strip()
            .str.replace(
                "Re-Entering",
                "Re-entering",
                regex=False
            )
        )

        result["Risk_Model"] = (
            X["Risk_Model"]
            .astype("string")
            .str.strip()
        )

        result["Rev_Exp_Cat"] = (
            X["Rev_Exp_Cat"]
            .astype("string")
            .str.strip()
        )

        return result


# ============================================================
# PREPARE TARGET METRICS
# ============================================================

def prepare_reference(df):

    reference = df.copy().reset_index(drop=True)

    # ---------------------------------------------------------
    # Savings percentage
    # ---------------------------------------------------------

    savings = np.where(
        reference["performance_year"].eq(2020),
        reference["Sav_rate"] * 100.0,
        reference["Sav_rate"]
    )

    reference["SavingsPct"] = pd.Series(
        savings,
        index=reference.index
    )

    # 2021 fallback and any other missing values
    reference["SavingsPct"] = (
        reference["SavingsPct"]
        .fillna(reference["Sav_Rate"])
    )

    # Final mathematical fallback
    calculated_savings = (
        (
            reference["ABtotBnchmk"]
            - reference["ABtotExp"]
        )
        / reference["ABtotBnchmk"]
        * 100.0
    )

    reference["SavingsPct"] = (
        reference["SavingsPct"]
        .fillna(calculated_savings)
    )

    # ---------------------------------------------------------
    # Quality
    # ---------------------------------------------------------

    quality = pd.to_numeric(
        reference["QualScore"],
        errors="coerce"
    )

    # Same-year median
    year_median = quality.groupby(
        reference["performance_year"]
    ).transform("median")

    quality = quality.fillna(year_median)

    # Overall median fallback
    quality = quality.fillna(quality.median())

    reference["QualScore"] = quality

    # ---------------------------------------------------------
    # PMPM
    # ---------------------------------------------------------

    reference["PMPM"] = (
        pd.to_numeric(
            reference["ABtotExp"],
            errors="coerce"
        )
        /
        pd.to_numeric(
            reference["N_AB"],
            errors="coerce"
        )
        / 12.0
    )

    return reference


# ============================================================
# BUILD COMPLETE ML PIPELINE
# ============================================================

def build_pipeline(number_of_rows):

    # Numeric preprocessing
    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                )
            ),
            (
                "scaler",
                StandardScaler()
            ),
        ]
    )

    # Categorical preprocessing
    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent"
                )
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False
                )
            ),
        ]
    )

    # Combine numeric + categorical
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_pipeline,
                NUMERIC_FEATURES
            ),
            (
                "categorical",
                categorical_pipeline,
                CATEGORICAL_FEATURES
            ),
        ]
    )

    # Complete pipeline
    pipeline = Pipeline(
        steps=[
            (
                "feature_engineer",
                PeerFeatureEngineer()
            ),
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                NearestNeighbors(
                    n_neighbors=number_of_rows,
                    metric="euclidean"
                )
            ),
        ]
    )

    return pipeline


# ============================================================
# PEER TARGET MODEL
# ============================================================

class PeerTargetModel:

    def __init__(
        self,
        pipeline,
        reference_df
    ):
        self.pipeline = pipeline
        self.reference_df = (
            reference_df
            .reset_index(drop=True)
        )

    def predict(
        self,
        aco_id,
        performance_year=None,
        top_k=3
    ):

        reference = self.reference_df

        # Find target ACO
        target_rows = reference[
            reference["ACO_ID"].astype(str)
            == str(aco_id)
        ]

        if target_rows.empty:
            raise ValueError(
                f"ACO_ID '{aco_id}' was not found."
            )

        # If year isn't provided, use latest year
        if performance_year is None:
            performance_year = int(
                target_rows["performance_year"].max()
            )

        target = target_rows[
            target_rows["performance_year"]
            == int(performance_year)
        ]

        if target.empty:
            raise ValueError(
                f"ACO_ID '{aco_id}' has no data "
                f"for year {performance_year}."
            )

        target_row = target.iloc[0]

        # -----------------------------------------------------
        # Transform target using the COMPLETE pipeline
        # -----------------------------------------------------

        transformed_target = (
            self.pipeline[:-1].transform(target)
        )

        # Find all nearest neighbors
        distances, indices = (
            self.pipeline
            .named_steps["model"]
            .kneighbors(
                transformed_target,
                n_neighbors=len(reference)
            )
        )

        # Create candidate dataframe
        candidates = reference.iloc[
            indices[0]
        ].copy()

        candidates["distance"] = distances[0]

        # -----------------------------------------------------
        # SAME YEAR ONLY
        # -----------------------------------------------------

        candidates = candidates[
            candidates["performance_year"]
            == int(performance_year)
        ]

        # -----------------------------------------------------
        # REMOVE TARGET ONLY FROM PEER CANDIDATES
        # -----------------------------------------------------

        candidates = candidates[
            candidates["ACO_ID"].astype(str)
            != str(aco_id)
        ]

        candidates = candidates.sort_values(
            "distance"
        )

        if candidates.empty:
            raise ValueError(
                "No same-year peers were found."
            )

        # Look at the closest 30 similar ACOs
        # before selecting better performers.
        candidate_pool = candidates.head(
            max(30, top_k * 10)
        ).copy()

        # -----------------------------------------------------
        # BETTER PEER LOGIC
        # -----------------------------------------------------

        better_mask = (
            (
                candidate_pool["SavingsPct"]
                >= target_row["SavingsPct"]
            )
            &
            (
                candidate_pool["QualScore"]
                >= target_row["QualScore"]
            )
            &
            (
                candidate_pool["PMPM"]
                <= target_row["PMPM"]
            )
            &
            (
                (
                    candidate_pool["SavingsPct"]
                    > target_row["SavingsPct"]
                )
                |
                (
                    candidate_pool["QualScore"]
                    > target_row["QualScore"]
                )
                |
                (
                    candidate_pool["PMPM"]
                    < target_row["PMPM"]
                )
            )
        )

        better_peers = (
            candidate_pool[
                better_mask
            ]
            .head(top_k)
            .copy()
        )

        # -----------------------------------------------------
        # FALLBACK FOR HIGH PERFORMERS
        # -----------------------------------------------------

        if better_peers.empty:

            benchmark_peers = (
                candidates
                .head(top_k)
                .copy()
            )

            benchmark_source = (
                "similar_peers_fallback"
            )

        else:

            benchmark_peers = better_peers

            benchmark_source = (
                "better_similar_peers"
            )

        # -----------------------------------------------------
        # BENCHMARK
        # -----------------------------------------------------

        benchmark = {
            "savings_pct": round(
                float(
                    benchmark_peers[
                        "SavingsPct"
                    ].mean()
                ),
                2
            ),
            "quality": round(
                float(
                    benchmark_peers[
                        "QualScore"
                    ].mean()
                ),
                2
            ),
            "pmpm": round(
                float(
                    benchmark_peers[
                        "PMPM"
                    ].mean()
                ),
                2
            ),
        }

        # -----------------------------------------------------
        # TARGET
        # -----------------------------------------------------

        target_metrics = {
            "savings_pct": round(
                float(
                    target_row["SavingsPct"]
                ),
                2
            ),
            "quality": round(
                float(
                    target_row["QualScore"]
                ),
                2
            ),
            "pmpm": round(
                float(
                    target_row["PMPM"]
                ),
                2
            ),
        }

        # -----------------------------------------------------
        # GAPS
        # -----------------------------------------------------

        savings_gap = (
            target_metrics["savings_pct"]
            - benchmark["savings_pct"]
        )

        quality_gap = (
            target_metrics["quality"]
            - benchmark["quality"]
        )

        pmpm_gap = (
            target_metrics["pmpm"]
            - benchmark["pmpm"]
        )

        # -----------------------------------------------------
        # CLASSIFICATION
        # -----------------------------------------------------

        if (
            savings_gap >= 0
            and quality_gap >= 0
            and pmpm_gap <= 0
        ):

            classification = "High Performer"

            recommendation = (
                "Maintain current performance "
                "and capture best practices "
                "for continued performance."
            )

        elif (
            savings_gap >= 0
            and quality_gap < 0
            and pmpm_gap <= 0
        ):

            classification = (
                "Strong Performer — "
                "Quality Improvement Opportunity"
            )

            recommendation = (
                "Maintain strong savings and "
                "cost performance while improving "
                "quality toward the peer benchmark."
            )

        elif (
            savings_gap < 0
            and quality_gap >= 0
            and pmpm_gap <= 0
        ):

            classification = (
                "Strong Quality/Cost — "
                "Savings Improvement Opportunity"
            )

            recommendation = (
                "Maintain quality and PMPM "
                "performance while improving savings."
            )

        elif (
            savings_gap < 0
            and pmpm_gap > 0
        ):

            classification = (
                "Cost & Savings Improvement Opportunity"
            )

            recommendation = (
                "Focus on reducing PMPM and "
                "improving savings while protecting quality."
            )

        else:

            classification = "Needs Improvement"

            recommendation = (
                "Work on the metrics below peer "
                "benchmarks, prioritizing savings, "
                "quality, and PMPM together."
            )

        # -----------------------------------------------------
        # PEER OUTPUT
        # -----------------------------------------------------

        peer_output = benchmark_peers[
            [
                "ACO_ID",
                "ACO_Name",
                "SavingsPct",
                "QualScore",
                "PMPM",
                "distance",
            ]
        ].copy()

        peer_output = peer_output.rename(
            columns={
                "SavingsPct": "savings_pct",
                "QualScore": "quality",
                "PMPM": "pmpm",
            }
        )

        return {
            "target_aco": {
                "ACO_ID": str(
                    target_row["ACO_ID"]
                ),
                "ACO_Name": str(
                    target_row["ACO_Name"]
                ),
                "performance_year": int(
                    target_row["performance_year"]
                ),
                **target_metrics,
            },

            "similar_peers": (
                peer_output
                .to_dict(orient="records")
            ),

            "benchmark": benchmark,

            "gaps_vs_benchmark": {
                "savings_pct_gap": round(
                    float(savings_gap),
                    2
                ),
                "quality_gap": round(
                    float(quality_gap),
                    2
                ),
                "pmpm_gap": round(
                    float(pmpm_gap),
                    2
                ),
            },

            "classification": classification,

            "recommendation": recommendation,

            "benchmark_source": benchmark_source,
        }


# ============================================================
# TRAIN + SAVE
# ============================================================

def train_and_save(df):

    output_directory = (
        Path("ml")
        / "models"
        / "peer_target_finder"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    # Prepare data
    reference = prepare_reference(df)

    # Build complete pipeline
    pipeline = build_pipeline(
        len(reference)
    )

    # Train/f​​it similarity pipeline
    pipeline.fit(reference)

    # Package pipeline + reference data
    model = PeerTargetModel(
        pipeline=pipeline,
        reference_df=reference
    )

    # ---------------------------------------------------------
    # 1. model.pkl
    # ---------------------------------------------------------

    joblib.dump(
        model,
        output_directory / "model.pkl"
    )

    # ---------------------------------------------------------
    # 2. features.json
    # ---------------------------------------------------------

    features = {
        "features": (
            NUMERIC_FEATURES
            + CATEGORICAL_FEATURES
        )
    }

    with open(
        output_directory / "features.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            features,
            file,
            indent=2
        )

    # ---------------------------------------------------------
    # 3. model_info.json
    # ---------------------------------------------------------

    model_info = {
        "model_name": "aco_peer_target_finder",
        "version": "1.0",
        "model_type": "NearestNeighbors",
        "target": "Peer Benchmark (SavingsPct, QualScore, PMPM)",
    }

    with open(
        output_directory / "model_info.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            model_info,
            file,
            indent=2
        )

    print()
    print("======================================")
    print("PEER TARGET FINDER TRAINING COMPLETE")
    print("======================================")
    print(f"Rows used: {len(reference)}")
    print("model.pkl saved")
    print("features.json saved")
    print("model_info.json saved")
    print(f"Location: {output_directory}")


if __name__ == "__main__":
    print("peer_model.py contains the model definition.")
    print("Run train_peer_model.py to train the model.")