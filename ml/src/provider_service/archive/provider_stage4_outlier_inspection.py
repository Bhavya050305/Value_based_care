import pandas as pd
import numpy as np

# ============================================================
# PROVIDER STAGE 4 OUTLIER INSPECTION
# ============================================================

INPUT_PATH = "data/processed/provider_service/provider_features_stage4.csv"

print("=" * 70)
print("PROVIDER STAGE 4 OUTLIER INSPECTION")
print("=" * 70)

# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

print("\nLoading Stage 4 dataset...")

df = pd.read_csv(INPUT_PATH, low_memory=False)

print(f"Rows loaded: {len(df):,}")
print(f"Columns loaded: {len(df.columns)}")

# ------------------------------------------------------------
# 2. BASIC VALIDATION
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("BASIC VALIDATION")
print("=" * 70)

print(f"Duplicate NPI-Year rows: {df.duplicated(['Rndrng_NPI', 'Year']).sum():,}")
print(
    f"Unique NPI-Year combinations: "
    f"{df[['Rndrng_NPI', 'Year']].drop_duplicates().shape[0]:,}"
)

# ------------------------------------------------------------
# 3. FEATURES TO INSPECT
# ------------------------------------------------------------

outlier_features = [
    "service_intensity_per_beneficiary",
    "hcpcs_intensity_per_beneficiary",
    "services_per_condition_burden",
    "services_per_risk_score",
    "payment_efficiency",
    "standardized_payment_ratio",
    "payment_to_charge_ratio",
    "allowed_to_charge_ratio",
    "payment_vs_standardized_difference",
    "payment_vs_standardized_pct",
    "risk_adjusted_services",
    "risk_adjusted_payment",
    "risk_adjusted_allowed_amount",
    "condition_adjusted_payment",
    "condition_adjusted_services",
    "payment_per_risk_adjusted_beneficiary",
    "allowed_per_risk_adjusted_beneficiary",
    "medical_payment_per_service",
    "medical_allowed_per_service",
    "medical_payment_per_beneficiary",
    "drug_payment_per_service_stage4",
    "drug_allowed_per_service_stage4",
    "drug_payment_per_beneficiary_stage4",
]

available_features = [
    col for col in outlier_features
    if col in df.columns
]

print("\nFeatures available for outlier inspection:", len(available_features))

# ------------------------------------------------------------
# 4. NULL / INFINITE CHECK
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("NULL AND INFINITE VALUE CHECK")
print("=" * 70)

for col in available_features:

    null_count = df[col].isna().sum()

    numeric = pd.to_numeric(df[col], errors="coerce")

    infinite_count = np.isinf(numeric).sum()

    if null_count > 0 or infinite_count > 0:
        print(
            f"{col}: "
            f"nulls={null_count:,}, "
            f"infinite={infinite_count:,}"
        )

# ------------------------------------------------------------
# 5. DISTRIBUTION / PERCENTILES
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FEATURE DISTRIBUTION")
print("=" * 70)

percentiles = [
    0.00,
    0.25,
    0.50,
    0.75,
    0.90,
    0.95,
    0.99,
    0.995,
    0.999,
    1.00
]

for col in available_features:

    series = pd.to_numeric(df[col], errors="coerce").replace(
        [np.inf, -np.inf],
        np.nan
    ).dropna()

    if len(series) == 0:
        continue

    values = series.quantile(percentiles)

    print("\n" + col)

    for p, value in values.items():
        print(f"  P{p * 100:6.1f}: {value:,.6f}")

# ------------------------------------------------------------
# 6. EXTREME OBSERVATIONS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("EXTREME OBSERVATIONS")
print("=" * 70)

context_columns = [
    "Rndrng_NPI",
    "Rndrng_Prvdr_Last_Org_Name",
    "Rndrng_Prvdr_First_Name",
    "Rndrng_Prvdr_City",
    "Rndrng_Prvdr_State_Abrvtn",
    "Rndrng_Prvdr_Type",
    "Year",
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_HCPCS_Cds",
    "Tot_Mdcr_Pymt_Amt",
    "Tot_Mdcr_Alowd_Amt",
    "Bene_Avg_Risk_Scre",
    "average_risk_score",
    "overall_condition_burden",
]

context_columns = [
    col for col in context_columns
    if col in df.columns
]

# ------------------------------------------------------------
# 7. TOP 10 EXTREME VALUES FOR EACH IMPORTANT FEATURE
# ------------------------------------------------------------

important_features = [
    "service_intensity_per_beneficiary",
    "risk_adjusted_services",
    "risk_adjusted_payment",
    "condition_adjusted_payment",
]

for feature in important_features:

    if feature not in df.columns:
        continue

    print("\n" + "-" * 70)
    print(f"TOP 10 EXTREME VALUES: {feature}")
    print("-" * 70)

    temp = df[
        context_columns + [feature]
    ].copy()

    temp[feature] = pd.to_numeric(
        temp[feature],
        errors="coerce"
    )

    temp = temp.replace(
        [np.inf, -np.inf],
        np.nan
    ).dropna(subset=[feature])

    temp = temp.sort_values(
        feature,
        ascending=False
    ).head(10)

    print(
        temp.to_string(
            index=False
        )
    )

# ------------------------------------------------------------
# 8. DENOMINATOR INSPECTION
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("DENOMINATOR INSPECTION")
print("=" * 70)

denominator_columns = [
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_HCPCS_Cds",
    "Bene_Avg_Risk_Scre",
    "average_risk_score",
    "overall_condition_burden",
]

for col in denominator_columns:

    if col not in df.columns:
        continue

    series = pd.to_numeric(
        df[col],
        errors="coerce"
    )

    print(f"\n{col}")

    print(f"  Null:  {series.isna().sum():,}")
    print(f"  Zero:  {(series == 0).sum():,}")
    print(f"  <= 1:  {(series <= 1).sum():,}")
    print(f"  <= 5:  {(series <= 5).sum():,}")
    print(f"  <= 10: {(series <= 10).sum():,}")

# ------------------------------------------------------------
# 9. EXTREME SERVICE INTENSITY + DENOMINATOR
# ------------------------------------------------------------

if "service_intensity_per_beneficiary" in df.columns:

    print("\n" + "=" * 70)
    print("SERVICE INTENSITY DENOMINATOR ANALYSIS")
    print("=" * 70)

    temp = df.copy()

    temp["service_intensity_per_beneficiary"] = pd.to_numeric(
        temp["service_intensity_per_beneficiary"],
        errors="coerce"
    )

    temp = temp.replace(
        [np.inf, -np.inf],
        np.nan
    )

    temp = temp.sort_values(
        "service_intensity_per_beneficiary",
        ascending=False
    )

    cols = [
        "Rndrng_NPI",
        "Year",
        "Rndrng_Prvdr_Last_Org_Name",
        "Tot_Benes",
        "Tot_Srvcs",
        "Tot_HCPCS_Cds",
        "service_intensity_per_beneficiary",
    ]

    cols = [
        col for col in cols
        if col in temp.columns
    ]

    print(
        temp[cols]
        .head(20)
        .to_string(index=False)
    )

# ------------------------------------------------------------
# 10. FLAG EXTREME OBSERVATIONS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("EXTREME VALUE COUNTS")
print("=" * 70)

for col in important_features:

    if col not in df.columns:
        continue

    series = pd.to_numeric(
        df[col],
        errors="coerce"
    )

    series = series.replace(
        [np.inf, -np.inf],
        np.nan
    )

    valid = series.dropna()

    if len(valid) == 0:
        continue

    p99 = valid.quantile(0.99)
    p995 = valid.quantile(0.995)
    p999 = valid.quantile(0.999)

    print(f"\n{col}")
    print(f"  > P99:  {(valid > p99).sum():,}")
    print(f"  > P99.5:{(valid > p995).sum():,}")
    print(f"  > P99.9:{(valid > p999).sum():,}")

# ------------------------------------------------------------
# 11. NEGATIVE VALUE CHECK
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("NEGATIVE VALUE CHECK")
print("=" * 70)

for col in available_features:

    series = pd.to_numeric(
        df[col],
        errors="coerce"
    )

    negative_count = (series < 0).sum()

    if negative_count > 0:

        print(
            f"{col}: "
            f"{negative_count:,} negative values"
        )

# ------------------------------------------------------------
# 12. FINAL CONCLUSION
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("OUTLIER INSPECTION COMPLETED")
print("=" * 70)

print("""
IMPORTANT:

This script DOES NOT modify the dataset.
This script DOES NOT remove outliers.
This script DOES NOT cap or winsorize values.
This script DOES NOT transform features.

It only identifies extreme values and investigates
whether they are associated with small denominators
or potentially unusual provider observations.

NEXT STEP:
Review the output before deciding on outlier treatment.
""")