import os
import json
import numpy as np
import pandas as pd
import joblib

from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# 1. LOAD ENVIRONMENT
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL is missing from .env")

if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY is missing from .env")


# ============================================================
# 2. SUPABASE CLIENT
# ============================================================

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

print("Supabase client created successfully!")


# ============================================================
# 3. LOAD TRAINED MODEL
# ============================================================

MODEL_PATH = os.path.join(
    "ml",
    "models",
    "peer_target_finder",
    "model.pkl"
)

print()
print("Loading trained Peer Target Finder model...")

model = joblib.load(MODEL_PATH)

print("Model loaded successfully!")


# ============================================================
# 4. LOAD MODEL FEATURES
# ============================================================

FEATURES_PATH = os.path.join(
    "ml",
    "models",
    "peer_target_finder",
    "features.json"
)

with open(
    FEATURES_PATH,
    "r",
    encoding="utf-8"
) as file:

    feature_info = json.load(file)

MODEL_FEATURES = feature_info["features"]

print()
print(
    "Number of model features:",
    len(MODEL_FEATURES)
)


# ============================================================
# 5. LOAD ALL DATA FROM SUPABASE
# ============================================================

def load_aco_data(batch_size=1000):

    all_rows = []
    start = 0

    while True:

        response = (
            supabase
            .table("fact_aco_performance")
            .select("*")
            .range(
                start,
                start + batch_size - 1
            )
            .execute()
        )

        rows = response.data

        if not rows:
            break

        all_rows.extend(rows)

        print(
            f"Loaded {len(all_rows)} rows"
        )

        if len(rows) < batch_size:
            break

        start += batch_size

    return pd.DataFrame(all_rows)


print()
print("Loading ACO data from Supabase...")

df = load_aco_data()

print()
print("Dataset loaded successfully.")
print("Shape:", df.shape)


# ============================================================
# 6. PREPARE TARGET METRICS
# EXACTLY MATCH peer_model.py
# ============================================================

reference = df.copy().reset_index(drop=True)


# ------------------------------------------------------------
# SavingsPct
# ------------------------------------------------------------

reference["SavingsPct"] = np.where(
    reference["performance_year"].eq(2020),
    pd.to_numeric(
        reference["Sav_rate"],
        errors="coerce"
    ) * 100.0,

    pd.to_numeric(
        reference["Sav_rate"],
        errors="coerce"
    )
)


reference["SavingsPct"] = (
    reference["SavingsPct"]
    .fillna(
        pd.to_numeric(
            reference["Sav_Rate"],
            errors="coerce"
        )
    )
)


calculated_savings = (
    (
        pd.to_numeric(
            reference["ABtotBnchmk"],
            errors="coerce"
        )
        -
        pd.to_numeric(
            reference["ABtotExp"],
            errors="coerce"
        )
    )
    /
    pd.to_numeric(
        reference["ABtotBnchmk"],
        errors="coerce"
    )
    * 100.0
)


reference["SavingsPct"] = (
    reference["SavingsPct"]
    .fillna(calculated_savings)
)


# ------------------------------------------------------------
# Quality
# ------------------------------------------------------------

quality = pd.to_numeric(
    reference["QualScore"],
    errors="coerce"
)


year_median = (
    quality
    .groupby(
        reference["performance_year"]
    )
    .transform("median")
)


quality = quality.fillna(year_median)

quality = quality.fillna(
    quality.median()
)

reference["QualScore"] = quality


# ------------------------------------------------------------
# PMPM
# ------------------------------------------------------------

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
    /
    12.0
)


# ============================================================
# 7. GET ENGINEERED FEATURE VALUES
# USING THE SAME FEATURE ENGINEER
# FROM THE TRAINED MODEL
# ============================================================

print()
print("Creating exact engineered features...")

feature_engineer = (
    model.pipeline
    .named_steps["feature_engineer"]
)

engineered = feature_engineer.transform(
    reference
)


# ============================================================
# 8. GET EXACT PREPROCESSED MODEL INPUT
# ============================================================

print()
print(
    "Creating exact transformed model values..."
)

preprocessor = (
    model.pipeline
    .named_steps["preprocessor"]
)

transformed = preprocessor.transform(
    engineered
)


# ============================================================
# 9. GET FINAL MODEL FEATURE NAMES
# ============================================================

try:

    transformed_feature_names = (
        preprocessor
        .get_feature_names_out()
        .tolist()
    )

except Exception:

    transformed_feature_names = [
        f"model_feature_{i}"
        for i in range(
            transformed.shape[1]
        )
    ]


print(
    "Final transformed feature count:",
    len(transformed_feature_names)
)


# ============================================================
# 10. CREATE ENGINEERED FEATURE DATAFRAME
# ============================================================

engineered_df = engineered.copy()

engineered_df.index = reference.index


# ============================================================
# 11. FUNCTION TO CONVERT VALUES TO JSON SAFE VALUES
# ============================================================

def json_safe(value):

    if pd.isna(value):
        return None

    if isinstance(
        value,
        (np.integer, np.floating)
    ):
        return float(value)

    return str(value)


# ============================================================
# 12. CREATE COMPLETE RESULTS
# ============================================================

results = []

print()
print("Running Peer Target Finder for every ACO-year...")


for index in range(
    len(reference)
):

    target_row = reference.iloc[index]

    aco_id = str(
        target_row["ACO_ID"]
    )

    year = int(
        target_row["performance_year"]
    )

    try:

        # ====================================================
        # RUN THE SAME MODEL LOGIC
        # ====================================================

        result = model.predict(
            aco_id,
            year,
            top_k=3
        )


        # ====================================================
        # TARGET
        # ====================================================

        target = result["target_aco"]


        # ====================================================
        # BENCHMARK / PEER TARGET
        # ====================================================

        benchmark = result["benchmark"]


        # ====================================================
        # GAPS
        # ====================================================

        gaps = result[
            "gaps_vs_benchmark"
        ]


        # ====================================================
        # SIMILAR PEERS
        # ====================================================

        peers = result[
            "similar_peers"
        ]


        # ====================================================
        # ENGINEERED FEATURES
        # ====================================================

        feature_row = engineered_df.iloc[
            index
        ]


        # ====================================================
        # EXACT TRANSFORMED MODEL VALUES
        # ====================================================

        transformed_row = transformed[
            index
        ]


        model_input_values = {}

        for i, feature_name in enumerate(
            transformed_feature_names
        ):

            model_input_values[
                feature_name
            ] = float(
                transformed_row[i]
            )


        # ====================================================
        # COMPLETE DATABASE RECORD
        # ====================================================

        record = {

            "ml_model_name":
                "aco_peer_target_finder",

            "aco_id":
                target["ACO_ID"],

            "aco_name":
                target["ACO_Name"],

            "performance_year":
                target["performance_year"],


            # ================================================
            # 24 ENGINEERED FEATURES
            # ================================================

            "log_n_ab":
                json_safe(
                    feature_row["log_N_AB"]
                ),

            "log_pmpm":
                json_safe(
                    feature_row["log_PMPM"]
                ),

            "cms_hcc_riskscore_esrd_py":
                json_safe(
                    feature_row[
                        "CMS_HCC_RiskScore_ESRD_PY"
                    ]
                ),

            "cms_hcc_riskscore_dis_py":
                json_safe(
                    feature_row[
                        "CMS_HCC_RiskScore_DIS_PY"
                    ]
                ),

            "cms_hcc_riskscore_agdu_py":
                json_safe(
                    feature_row[
                        "CMS_HCC_RiskScore_AGDU_PY"
                    ]
                ),

            "cms_hcc_riskscore_agnd_py":
                json_safe(
                    feature_row[
                        "CMS_HCC_RiskScore_AGND_PY"
                    ]
                ),

            "pct_age_0_64":
                json_safe(
                    feature_row[
                        "Pct_Age_0_64"
                    ]
                ),

            "pct_age_65_74":
                json_safe(
                    feature_row[
                        "Pct_Age_65_74"
                    ]
                ),

            "pct_age_75_84":
                json_safe(
                    feature_row[
                        "Pct_Age_75_84"
                    ]
                ),

            "pct_age_85plus":
                json_safe(
                    feature_row[
                        "Pct_Age_85plus"
                    ]
                ),

            "pct_female":
                json_safe(
                    feature_row[
                        "Pct_Female"
                    ]
                ),

            "pct_white":
                json_safe(
                    feature_row[
                        "Pct_White"
                    ]
                ),

            "pct_black":
                json_safe(
                    feature_row[
                        "Pct_Black"
                    ]
                ),

            "pct_race_other":
                json_safe(
                    feature_row[
                        "Pct_Race_Other"
                    ]
                ),

            "perc_dual":
                json_safe(
                    feature_row[
                        "Perc_Dual"
                    ]
                ),

            "ed_visits_per_ben":
                json_safe(
                    feature_row[
                        "ED_Visits_per_Ben"
                    ]
                ),

            "em_visits_per_ben":
                json_safe(
                    feature_row[
                        "EM_Visits_per_Ben"
                    ]
                ),

            "snf_adm_per_ben":
                json_safe(
                    feature_row[
                        "SNF_Adm_per_Ben"
                    ]
                ),

            "pcp_per_1000":
                json_safe(
                    feature_row[
                        "PCP_per_1000"
                    ]
                ),

            "spec_per_1000":
                json_safe(
                    feature_row[
                        "Spec_per_1000"
                    ]
                ),

            "hosp_per_1000":
                json_safe(
                    feature_row[
                        "Hosp_per_1000"
                    ]
                ),


            # ================================================
            # CATEGORICAL FEATURES
            # ================================================

            "agree_type":
                json_safe(
                    feature_row[
                        "Agree_Type"
                    ]
                ),

            "risk_model":
                json_safe(
                    feature_row[
                        "Risk_Model"
                    ]
                ),

            "rev_exp_cat":
                json_safe(
                    feature_row[
                        "Rev_Exp_Cat"
                    ]
                ),


            # ================================================
            # CURRENT TARGET ACO VALUES
            # ================================================

            "savings_pct":
                target["savings_pct"],

            "quality":
                target["quality"],

            "pmpm":
                target["pmpm"],


            # ================================================
            # PEER TARGET / BENCHMARK
            # ================================================

            "peer_target_savings_pct":
                benchmark["savings_pct"],

            "peer_target_quality":
                benchmark["quality"],

            "peer_target_pmpm":
                benchmark["pmpm"],


            # ================================================
            # GAPS
            # ================================================

            "savings_pct_gap":
                gaps["savings_pct_gap"],

            "quality_gap":
                gaps["quality_gap"],

            "pmpm_gap":
                gaps["pmpm_gap"],


            # ================================================
            # DECISION OUTPUT
            # ================================================

            "classification":
                result["classification"],

            "recommendation":
                result["recommendation"],

            "benchmark_source":
                result["benchmark_source"],


            # ================================================
            # SELECTED PEERS
            # ================================================

            "similar_peers":
                peers,


            # ================================================
            # EXACT MODEL INPUT
            # ================================================

            "model_input_values":
                model_input_values,

            "model_input_feature_names":
                transformed_feature_names
        }


        results.append(record)


    except Exception as error:

        print()
        print(
            "ERROR processing:",
            aco_id,
            year
        )

        print(error)


    # Progress message

    if len(results) % 100 == 0:

        print(
            f"Processed {len(results)} rows..."
        )


# ============================================================
# 13. CHECK RESULTS
# ============================================================

print()
print(
    "=========================================="
)

print(
    "PEER TARGET RESULTS CREATED"
)

print(
    "=========================================="
)

print(
    "Rows successfully processed:",
    len(results)
)


# ============================================================
# 14. DELETE OLD RESULTS
# ============================================================

TABLE_NAME = (
    "peer_target_finder_results"
)

print()
print(
    "Removing previous Peer Target Finder results..."
)

(
    supabase
    .table(TABLE_NAME)
    .delete()
    .eq(
        "ml_model_name",
        "aco_peer_target_finder"
    )
    .execute()
)


# ============================================================
# 15. INSERT RESULTS IN BATCHES
# ============================================================

print()
print(
    "Uploading results to Supabase..."
)

BATCH_SIZE = 100

total_inserted = 0


for start in range(
    0,
    len(results),
    BATCH_SIZE
):

    batch = results[
        start:start + BATCH_SIZE
    ]

    response = (
        supabase
        .table(TABLE_NAME)
        .insert(batch)
        .execute()
    )

    total_inserted += len(
        response.data
    )

    print(
        f"Inserted {total_inserted} / "
        f"{len(results)}"
    )


# ============================================================
# 16. FINAL MESSAGE
# ============================================================

print()
print(
    "=========================================="
)

print(
    "UPLOAD COMPLETE"
)

print(
    "=========================================="
)

print()
print(
    "Table:",
    TABLE_NAME
)

print(
    "Rows:",
    total_inserted
)

print()
print(
    "Each row contains:"
)

print(
    "✓ ACO ID"
)

print(
    "✓ ACO Name"
)

print(
    "✓ Performance Year"
)

print(
    "✓ 24 ML features"
)

print(
    "✓ Current Savings"
)

print(
    "✓ Current Quality"
)

print(
    "✓ Current PMPM"
)

print(
    "✓ Peer Target Savings"
)

print(
    "✓ Peer Target Quality"
)

print(
    "✓ Peer Target PMPM"
)

print(
    "✓ Savings Gap"
)

print(
    "✓ Quality Gap"
)

print(
    "✓ PMPM Gap"
)

print(
    "✓ Classification"
)

print(
    "✓ Recommendation"
)

print(
    "✓ Benchmark Source"
)

print(
    "✓ Similar Peers"
)

print(
    "✓ Exact transformed model values"
)

print()
print("DONE!")