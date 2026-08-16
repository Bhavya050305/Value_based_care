from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# PROVIDER SUPPRESSION / COMPONENT CROSSCHECK
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "provider_features_stage4.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "provider_service"
    / "diagnostics"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


print("=" * 80)
print("PROVIDER SUPPRESSION / COMPONENT CROSSCHECK")
print("=" * 80)

print(f"Input file : {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)

print(f"Rows loaded: {len(df):,}")


# ------------------------------------------------------------
# REQUIRED COLUMNS
# ------------------------------------------------------------

required_columns = [
    "Rndrng_NPI",
    "Year",
    "Tot_Mdcr_Pymt_Amt",
    "Tot_Srvcs",
    "Med_Mdcr_Pymt_Amt",
    "Drug_Mdcr_Pymt_Amt",
    "Med_Tot_Srvcs",
    "Drug_Tot_Srvcs",
    "drug_data_suppressed",
]

missing = [
    c for c in required_columns
    if c not in df.columns
]

if missing:
    raise ValueError(
        "Missing required columns:\n"
        + "\n".join(f" - {c}" for c in missing)
    )


# ------------------------------------------------------------
# COMPONENT DIFFERENCES
# ------------------------------------------------------------

df["component_payment_sum"] = (
    df["Med_Mdcr_Pymt_Amt"]
    + df["Drug_Mdcr_Pymt_Amt"]
)

df["component_service_sum"] = (
    df["Med_Tot_Srvcs"]
    + df["Drug_Tot_Srvcs"]
)

df["payment_difference"] = (
    df["component_payment_sum"]
    - df["Tot_Mdcr_Pymt_Amt"]
)

df["service_difference"] = (
    df["component_service_sum"]
    - df["Tot_Srvcs"]
)


df["payment_mismatch"] = (
    ~np.isclose(
        df["component_payment_sum"],
        df["Tot_Mdcr_Pymt_Amt"],
        rtol=1e-9,
        atol=1e-6,
    )
)

df["service_mismatch"] = (
    ~np.isclose(
        df["component_service_sum"],
        df["Tot_Srvcs"],
        rtol=1e-9,
        atol=1e-6,
    )
)


# ------------------------------------------------------------
# SUPPRESSION CROSS-TAB
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("SUPPRESSION CROSSCHECK")
print("=" * 80)

crosscheck = (
    df.groupby("drug_data_suppressed")
    .agg(
        rows=("Rndrng_NPI", "size"),
        payment_mismatch_rows=("payment_mismatch", "sum"),
        service_mismatch_rows=("service_mismatch", "sum"),
        payment_mismatch_pct=("payment_mismatch", "mean"),
        service_mismatch_pct=("service_mismatch", "mean"),
    )
    .reset_index()
)

crosscheck["payment_mismatch_pct"] *= 100
crosscheck["service_mismatch_pct"] *= 100

print(crosscheck.to_string(index=False))


# ------------------------------------------------------------
# MEDICAL > TOTAL BY SUPPRESSION
# ------------------------------------------------------------

df["medical_payment_gt_total"] = (
    df["Med_Mdcr_Pymt_Amt"]
    > df["Tot_Mdcr_Pymt_Amt"]
)

df["medical_service_gt_total"] = (
    df["Med_Tot_Srvcs"]
    > df["Tot_Srvcs"]
)


print("\n" + "=" * 80)
print("MEDICAL > TOTAL CROSSCHECK")
print("=" * 80)

medical_crosscheck = (
    df.groupby("drug_data_suppressed")
    .agg(
        rows=("Rndrng_NPI", "size"),
        medical_payment_gt_total=(
            "medical_payment_gt_total",
            "sum",
        ),
        medical_service_gt_total=(
            "medical_service_gt_total",
            "sum",
        ),
    )
    .reset_index()
)

print(medical_crosscheck.to_string(index=False))


# ------------------------------------------------------------
# SUPPRESSION + EXACT COMPONENT BEHAVIOR
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("SUPPRESSED ROW COMPONENT BEHAVIOR")
print("=" * 80)

suppressed = df[
    df["drug_data_suppressed"] == True
].copy()

print(
    f"Suppressed rows: {len(suppressed):,}"
)

print(
    "\nDrug service values:"
)

print(
    suppressed["Drug_Tot_Srvcs"]
    .value_counts(dropna=False)
    .head(10)
    .to_string()
)

print(
    "\nDrug payment values:"
)

print(
    suppressed["Drug_Mdcr_Pymt_Amt"]
    .value_counts(dropna=False)
    .head(10)
    .to_string()
)


# ------------------------------------------------------------
# EXAMPLES
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("SUPPRESSED ROW EXAMPLES")
print("=" * 80)

example_columns = [
    "Rndrng_NPI",
    "Year",
    "drug_data_suppressed",
    "Tot_Mdcr_Pymt_Amt",
    "Med_Mdcr_Pymt_Amt",
    "Drug_Mdcr_Pymt_Amt",
    "payment_difference",
    "Tot_Srvcs",
    "Med_Tot_Srvcs",
    "Drug_Tot_Srvcs",
    "service_difference",
]

print(
    df[
        df["drug_data_suppressed"] == True
    ][example_columns]
    .head(20)
    .to_string(index=False)
)


# ------------------------------------------------------------
# SAVE CROSSCHECK
# ------------------------------------------------------------

crosscheck.to_csv(
    OUTPUT_DIR
    / "provider_suppression_component_crosscheck.csv",
    index=False,
)

medical_crosscheck.to_csv(
    OUTPUT_DIR
    / "provider_suppression_medical_crosscheck.csv",
    index=False,
)


# ------------------------------------------------------------
# FINAL
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)

print(
    "No rows were removed."
)

print(
    "No values were capped."
)

print(
    "No outlier treatment was performed."
)

print(
    f"Output directory: {OUTPUT_DIR}"
)