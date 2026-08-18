import os
import numpy as np
import pandas as pd

# ============================================================
# FAST SYNTHETIC SERVICE DATA GENERATOR
# ============================================================

INPUT_FILE = r".\data\processed\provider_service\provider_dashboard_analytics.csv"
OUTPUT_FILE = r".\data\processed\provider_service\synthetic_service_data.csv"

SEED = 42
rng = np.random.default_rng(SEED)

print("=" * 70)
print("FAST SYNTHETIC SERVICE DATA GENERATION")
print("=" * 70)

# ------------------------------------------------------------
# 1. LOAD PROVIDER DATA
# ------------------------------------------------------------

print("\nLoading provider dashboard analytics...")

columns = [
    "Rndrng_NPI",
    "Year",
    "ACO_ID",
    "services_per_beneficiary",
    "utilization_score",
    "payment_per_service",
    "payment_per_beneficiary",
    "cost_score",
]

df = pd.read_csv(
    INPUT_FILE,
    usecols=columns
)

print("Rows loaded:", len(df))
print("Columns loaded:", len(df.columns))

# ------------------------------------------------------------
# 2. VALIDATION
# ------------------------------------------------------------

if df[["Rndrng_NPI", "Year"]].duplicated().sum() != 0:
    raise ValueError("Duplicate Provider-Year records found.")

if df["ACO_ID"].isna().sum() != 0:
    raise ValueError("Missing ACO_ID values found.")

print("Provider-Year grain check: PASSED")
print("ACO mapping check: PASSED")

# ------------------------------------------------------------
# 3. SERVICE CATALOG
# ------------------------------------------------------------

services = pd.DataFrame([
    ["99213", "Established Patient Office Visit", "OFFICE", "Primary Care", 95],
    ["99214", "Established Patient Office Visit - Moderate Complexity", "OFFICE", "Primary Care", 145],
    ["99215", "Established Patient Office Visit - High Complexity", "OFFICE", "Primary Care", 210],
    ["99203", "New Patient Office Visit", "OFFICE", "Specialist", 180],
    ["99204", "New Patient Office Visit - Moderate Complexity", "OFFICE", "Specialist", 260],
    ["99285", "Emergency Department Visit - High Complexity", "EMERGENCY", "Emergency", 420],
    ["99223", "Initial Hospital Care", "INPATIENT", "Hospital", 650],
    ["99232", "Subsequent Hospital Care", "INPATIENT", "Hospital", 450],
    ["71046", "Chest X-Ray", "OUTPATIENT", "Diagnostic", 120],
    ["93000", "Electrocardiogram", "OFFICE", "Diagnostic", 90],
    ["80053", "Comprehensive Metabolic Panel", "OUTPATIENT", "Laboratory", 75],
    ["83036", "Hemoglobin A1c Test", "OUTPATIENT", "Chronic Care", 65],
    ["36415", "Venipuncture", "OFFICE", "Laboratory", 35],
    ["99490", "Chronic Care Management", "OFFICE", "Chronic Care", 80],
    ["G0439", "Annual Wellness Visit", "OFFICE", "Preventive Care", 120],
], columns=[
    "HCPCS_Cd",
    "HCPCS_Desc",
    "Place_Of_Srvc",
    "service_category",
    "base_cost"
])

print("\nService types:", len(services))

# ------------------------------------------------------------
# 4. CREATE 5 SERVICE RECORDS PER PROVIDER-YEAR
# ------------------------------------------------------------

print("\nGenerating provider-service records...")

n = len(df)

# Five services per provider-year
# ------------------------------------------------------------
# 4. CREATE 5 UNIQUE SERVICES PER PROVIDER-YEAR
# ------------------------------------------------------------

print("\nGenerating provider-service records...")

n = len(df)
service_count = 5

# Create a random permutation of the 15 services
# for every provider-year.
service_indices = np.empty(
    (n, service_count),
    dtype=int
)

for i in range(n):
    service_indices[i] = rng.choice(
        len(services),
        size=service_count,
        replace=False
    )

service_index = service_indices.reshape(-1)

# Repeat each provider-year exactly 5 times
out = df.loc[
    df.index.repeat(service_count)
].reset_index(drop=True)

service = services.iloc[
    service_index
].reset_index(drop=True)

# Repeat provider rows five times
out = df.loc[
    df.index.repeat(5)
].reset_index(drop=True)

service = services.iloc[
    service_index
].reset_index(drop=True)

# ------------------------------------------------------------
# 5. MAP SERVICE INFORMATION
# ------------------------------------------------------------

out["HCPCS_Cd"] = service["HCPCS_Cd"].values
out["HCPCS_Desc"] = service["HCPCS_Desc"].values
out["Place_Of_Srvc"] = service["Place_Of_Srvc"].values
out["service_category"] = service["service_category"].values
out["base_cost"] = service["base_cost"].values

# ------------------------------------------------------------
# 6. CLEAN PROVIDER FEATURES
# ------------------------------------------------------------

util = pd.to_numeric(
    out["utilization_score"],
    errors="coerce"
).fillna(0.5).clip(0, 1)

cost = pd.to_numeric(
    out["cost_score"],
    errors="coerce"
).fillna(0.5).clip(0, 1)

services_per_bene = pd.to_numeric(
    out["services_per_beneficiary"],
    errors="coerce"
).fillna(2.5).clip(1, 20)

provider_payment = pd.to_numeric(
    out["payment_per_service"],
    errors="coerce"
).fillna(50).clip(1, 5000)

provider_payment_bene = pd.to_numeric(
    out["payment_per_beneficiary"],
    errors="coerce"
).fillna(150).clip(1, 100000)

# ------------------------------------------------------------
# 7. RANDOM VARIATION
# ------------------------------------------------------------

random_factor = rng.uniform(
    0.75,
    1.25,
    size=len(out)
)

# ------------------------------------------------------------
# 8. BENEFICIARIES
# ------------------------------------------------------------

estimated_benes = (
    provider_payment_bene /
    provider_payment
).clip(5, 5000)

out["Tot_Benes"] = np.maximum(
    1,
    (
        estimated_benes *
        (0.60 + 0.80 * util) *
        random_factor
    ).round()
).astype(int)

# ------------------------------------------------------------
# 9. SERVICE VOLUME
# ------------------------------------------------------------

out["Tot_Srvcs"] = np.maximum(
    out["Tot_Benes"],
    (
        out["Tot_Benes"] *
        services_per_bene *
        (0.65 + 0.90 * util) *
        random_factor
    ).round()
).astype(int)

out["Tot_Srvcs"] = out["Tot_Srvcs"].clip(
    1,
    100000
)

# ------------------------------------------------------------
# 10. COST VALUES
# ------------------------------------------------------------

cost_multiplier = (
    0.65 +
    1.25 * cost
)

out["Avg_Mdcr_Pymt_Amt"] = (
    out["base_cost"] *
    cost_multiplier *
    random_factor
).clip(5, 5000)

out["Avg_Mdcr_Alowd_Amt"] = (
    out["Avg_Mdcr_Pymt_Amt"] *
    rng.uniform(
        1.15,
        1.40,
        len(out)
    )
)

out["Avg_Sbmtd_Chrg"] = (
    out["Avg_Mdcr_Alowd_Amt"] *
    rng.uniform(
        1.8,
        3.5,
        len(out)
    )
)

out["Avg_Mdcr_Stdzd_Amt"] = (
    out["Avg_Mdcr_Pymt_Amt"] *
    rng.uniform(
        0.90,
        1.10,
        len(out)
    )
)

# ------------------------------------------------------------
# 11. DERIVED SERVICE METRICS
# ------------------------------------------------------------

out["payment_per_service"] = (
    out["Avg_Mdcr_Pymt_Amt"]
).round(2)

out["payment_per_beneficiary"] = (
    out["Tot_Srvcs"] *
    out["Avg_Mdcr_Pymt_Amt"] /
    out["Tot_Benes"]
).round(2)

out["utilization_rate"] = (
    out["Tot_Srvcs"] /
    out["Tot_Benes"]
).round(4)

out["cost_score"] = np.clip(
    cost *
    rng.uniform(
        0.85,
        1.15,
        len(out)
    ),
    0,
    1
).round(4)

out["utilization_score"] = np.clip(
    util *
    rng.uniform(
        0.85,
        1.15,
        len(out)
    ),
    0,
    1
).round(4)

out["total_cost"] = (
    out["Tot_Srvcs"] *
    out["Avg_Mdcr_Pymt_Amt"]
).round(2)

out["provider_count"] = 1

# ------------------------------------------------------------
# 12. SELECT FINAL COLUMNS
# ------------------------------------------------------------

final_columns = [
    "Rndrng_NPI",
    "ACO_ID",
    "Year",
    "HCPCS_Cd",
    "HCPCS_Desc",
    "Place_Of_Srvc",
    "service_category",
    "Tot_Benes",
    "Tot_Srvcs",
    "Avg_Sbmtd_Chrg",
    "Avg_Mdcr_Alowd_Amt",
    "Avg_Mdcr_Pymt_Amt",
    "Avg_Mdcr_Stdzd_Amt",
    "payment_per_service",
    "payment_per_beneficiary",
    "utilization_rate",
    "cost_score",
    "utilization_score",
    "total_cost",
    "provider_count",
]

out = out[final_columns]

# ------------------------------------------------------------
# 13. VALIDATION
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("SERVICE DATA VALIDATION")
print("=" * 70)

print("Rows:", len(out))
print("Columns:", len(out.columns))
print("Unique providers:", out["Rndrng_NPI"].nunique())
print("Unique ACOs:", out["ACO_ID"].nunique())
print("Years:", sorted(out["Year"].unique()))
print("HCPCS codes:", out["HCPCS_Cd"].nunique())
print(
    "Service categories:",
    out["service_category"].nunique()
)

duplicates = out.duplicated(
    [
        "Rndrng_NPI",
        "ACO_ID",
        "Year",
        "HCPCS_Cd"
    ]
).sum()

print(
    "Duplicate Provider-Year-HCPCS:",
    duplicates
)

missing = out.isna().sum().sum()

print(
    "Total missing values:",
    missing
)

negative = (
    out.select_dtypes(include=np.number) < 0
).sum().sum()

print(
    "Total negative numeric values:",
    negative
)

# ------------------------------------------------------------
# 14. SAVE
# ------------------------------------------------------------

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

print("\nSaving dataset...")

out.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n" + "=" * 70)
print("SYNTHETIC SERVICE DATA CREATED")
print("=" * 70)

print(
    "Output:",
    os.path.abspath(OUTPUT_FILE)
)

print("Rows:", len(out))
print("Columns:", len(out.columns))

print("\nDONE")
print("=" * 70)