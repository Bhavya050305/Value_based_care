"""
STEP 1 — Build ACO anomaly features for TARGET_YEAR.

Purpose
-------
Builds one feature row per ACO for the selected performance year.

The script:
1. Loads shared financial / quality / utilization YoY features.
2. Loads ACO state with historical fallback.
3. Loads provider-level cost/utilization scores from provider_selection.
4. Gets provider state from provider_combined.
5. Calculates state-level provider variation.
6. Calculates readmission proxy YoY change.
7. Merges everything into the final feature table.
8. Saves only TARGET_YEAR rows to aco_anomaly_features.
9. Preserves all existing years in the table.

IMPORTANT
---------
Do NOT use if_exists="replace".

The table may already contain 2023 features.
For 2022, this script deletes only existing 2022 rows
and appends the newly generated 2022 rows.
"""

import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sqlalchemy import text

from db import engine, TARGET_YEAR


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_TABLE = "aco_anomaly_features"

os.makedirs("plots", exist_ok=True)


# ============================================================
# STARTUP
# ============================================================

print("=" * 70)
print("BUILDING ACO ANOMALY FEATURES")
print("=" * 70)

print(f"Target performance year: {TARGET_YEAR}")
print(f"Database table: {OUTPUT_TABLE}")

print("=" * 70)


# ============================================================
# STATE NORMALIZATION
# ============================================================

def normalize_state(value):
    """
    Normalize state names / abbreviations.

    Examples:
        California -> CA
        CA         -> CA
        Texas, USA -> TX
    """

    if pd.isna(value):
        return np.nan

    value = str(value).strip().upper()

    # Keep only first part if value contains commas
    value = value.split(",")[0].strip()

    state_map = {
        "ALABAMA": "AL",
        "ALASKA": "AK",
        "ARIZONA": "AZ",
        "ARKANSAS": "AR",
        "CALIFORNIA": "CA",
        "COLORADO": "CO",
        "CONNECTICUT": "CT",
        "DELAWARE": "DE",
        "FLORIDA": "FL",
        "GEORGIA": "GA",
        "HAWAII": "HI",
        "IDAHO": "ID",
        "ILLINOIS": "IL",
        "INDIANA": "IN",
        "IOWA": "IA",
        "KANSAS": "KS",
        "KENTUCKY": "KY",
        "LOUISIANA": "LA",
        "MAINE": "ME",
        "MARYLAND": "MD",
        "MASSACHUSETTS": "MA",
        "MICHIGAN": "MI",
        "MINNESOTA": "MN",
        "MISSISSIPPI": "MS",
        "MISSOURI": "MO",
        "MONTANA": "MT",
        "NEBRASKA": "NE",
        "NEVADA": "NV",
        "NEW HAMPSHIRE": "NH",
        "NEW JERSEY": "NJ",
        "NEW MEXICO": "NM",
        "NEW YORK": "NY",
        "NORTH CAROLINA": "NC",
        "NORTH DAKOTA": "ND",
        "OHIO": "OH",
        "OKLAHOMA": "OK",
        "OREGON": "OR",
        "PENNSYLVANIA": "PA",
        "RHODE ISLAND": "RI",
        "SOUTH CAROLINA": "SC",
        "SOUTH DAKOTA": "SD",
        "TENNESSEE": "TN",
        "TEXAS": "TX",
        "UTAH": "UT",
        "VERMONT": "VT",
        "VIRGINIA": "VA",
        "WASHINGTON": "WA",
        "WEST VIRGINIA": "WV",
        "WISCONSIN": "WI",
        "WYOMING": "WY",
    }

    return state_map.get(value, value)


# ============================================================
# 1. SHARED SEGMENTATION FEATURES
# ============================================================

def load_shared_segmentation_features():

    print("\n" + "=" * 70)
    print("1. LOADING SHARED SEGMENTATION FEATURES")
    print("=" * 70)

    df = pd.read_sql(
        text(
            """
            SELECT
                "ACO_ID",
                performance_year,

                "GenSaveLossYoYPct"
                    AS savings_yoy_change_pct,

                "ExpenditureVariancePct"
                    AS expenditure_variance_pct,

                quality_change_yoy,
                ed_utilization_change_yoy,
                admission_change_yoy,
                em_utilization_change_yoy,
                advanced_imaging_change_yoy

            FROM aco_segmentation_ml_features

            WHERE performance_year = :yr
            """
        ),
        engine,
        params={"yr": TARGET_YEAR}
    )

    print(
        f"Shared segmentation features shape: {df.shape}"
    )

    print(
        f"Unique ACOs: {df['ACO_ID'].nunique()}"
    )

    print(
        f"Performance years: "
        f"{sorted(df['performance_year'].dropna().unique().tolist())}"
    )

    return df


# ============================================================
# 2. ACO STATES WITH HISTORICAL FALLBACK
# ============================================================

def load_aco_states():

    print("\n" + "=" * 70)
    print("2. LOADING ACO STATES")
    print("=" * 70)

    """
    ACO_State can be NULL for recent years.

    Therefore:
        - Look at all historical non-null ACO_State values.
        - Sort by ACO and year descending.
        - Keep the most recent known state for each ACO.

    This gives one reliable state per ACO.
    """

    df = pd.read_sql(
        text(
            """
            SELECT
                "ACO_ID",
                "ACO_State",
                performance_year

            FROM fact_aco_performance

            WHERE "ACO_State" IS NOT NULL

            ORDER BY
                "ACO_ID",
                performance_year DESC
            """
        ),
        engine
    )

    print(
        f"Raw non-null state records: {df.shape}"
    )

    # Most recent known state for each ACO
    df = df.drop_duplicates(
        subset="ACO_ID",
        keep="first"
    )

    df = df[
        [
            "ACO_ID",
            "ACO_State"
        ]
    ]

    # Normalize
    df["ACO_State"] = df["ACO_State"].apply(
        normalize_state
    )

    print(
        f"ACO states with fallback: {df.shape}"
    )

    print(
        f"Unique ACOs with known state: "
        f"{df['ACO_ID'].nunique()}"
    )

    print("\nACO state distribution:")

    print(
        df["ACO_State"]
        .value_counts(dropna=False)
        .head(20)
    )

    missing = df["ACO_State"].isna().sum()

    print("\nMissing ACO states:")
    print(missing)

    if missing == 0:
        print(
            "\nAll ACOs with a known historical state "
            "have been assigned a state successfully."
        )

    return df


# ============================================================
# 3. PROVIDER VARIATION
# ============================================================

def load_provider_variation():

    """
    Build provider-level variation by ACO state.

    Source:
        provider_selection
            ↓ rndrng_npi
        provider_by_npi
            ↓ provider state

    provider_selection contains:
        - aco_id
        - year
        - rndrng_npi
        - cost_score
        - utilization_score

    provider_by_npi contains:
        - Rndrng_NPI
        - Rndrng_Prvdr_State_Abrvtn

    The provider NPI join is complete for the available
    provider_selection records.
    """

    print(
        "\nLoading provider selection data..."
    )

    # --------------------------------------------------------
    # LOAD PROVIDER SELECTION
    # --------------------------------------------------------

    selection = pd.read_sql(
        f"""
        SELECT
            aco_id,
            year,
            rndrng_npi,
            provider_rank,
            selection_score,
            cost_score,
            utilization_score

        FROM provider_selection

        WHERE year = {TARGET_YEAR}

        ORDER BY
            aco_id,
            provider_rank
        """,
        engine
    )

    print(
        f"Provider selection rows: {selection.shape}"
    )

    print(
        "Unique ACOs:",
        selection["aco_id"].nunique()
    )

    print(
        "Performance year:",
        sorted(selection["year"].dropna().unique().tolist())
    )

    # --------------------------------------------------------
    # LOAD PROVIDER STATES
    # --------------------------------------------------------

    provider_states = pd.read_sql(
        """
        SELECT
            "Rndrng_NPI",
            "Rndrng_Prvdr_State_Abrvtn"

        FROM provider_by_npi

        WHERE "Rndrng_Prvdr_State_Abrvtn" IS NOT NULL
        """,
        engine
    )

    print(
        f"Provider state rows: {provider_states.shape}"
    )

    print(
        "Unique provider NPIs:",
        provider_states["Rndrng_NPI"].nunique()
    )

    # --------------------------------------------------------
    # NORMALIZE NPI TYPES
    # --------------------------------------------------------

    selection["rndrng_npi"] = (
        selection["rndrng_npi"]
        .astype(str)
        .str.strip()
    )

    provider_states["Rndrng_NPI"] = (
        provider_states["Rndrng_NPI"]
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # NORMALIZE PROVIDER STATES
    # --------------------------------------------------------

    provider_states["ACO_State"] = (
        provider_states[
            "Rndrng_Prvdr_State_Abrvtn"
        ]
        .apply(normalize_state)
    )

    # Keep only required columns
    provider_states = provider_states[
        [
            "Rndrng_NPI",
            "ACO_State"
        ]
    ]

    # Remove duplicate NPI records
    provider_states = provider_states.drop_duplicates(
        subset=["Rndrng_NPI"],
        keep="first"
    )

    # --------------------------------------------------------
    # JOIN PROVIDER SELECTION → PROVIDER STATE
    # --------------------------------------------------------

    merged = selection.merge(
        provider_states,
        left_on="rndrng_npi",
        right_on="Rndrng_NPI",
        how="left"
    )

    print(
        f"\nProvider rows after NPI/state join: "
        f"{merged.shape}"
    )

    known_state = merged["ACO_State"].notna().sum()
    missing_state = merged["ACO_State"].isna().sum()

    print(
        f"Providers with known state: "
        f"{known_state}"
    )

    print(
        f"Providers missing state: "
        f"{missing_state}"
    )

    # --------------------------------------------------------
    # CONVERT SCORES TO NUMERIC
    # --------------------------------------------------------

    merged["utilization_score"] = pd.to_numeric(
        merged["utilization_score"],
        errors="coerce"
    )

    merged["cost_score"] = pd.to_numeric(
        merged["cost_score"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # REMOVE RECORDS WITHOUT STATE
    # --------------------------------------------------------

    valid = merged[
        merged["ACO_State"].notna()
    ].copy()

    print(
        f"Provider rows with valid state: "
        f"{valid.shape}"
    )

    # --------------------------------------------------------
    # PROVIDER VARIATION BY STATE
    # --------------------------------------------------------

    agg = (
        valid
        .groupby(
            [
                "ACO_State",
                "year"
            ]
        )
        .agg(
            provider_utilization_variation=(
                "utilization_score",
                "std"
            ),

            provider_cost_variation=(
                "cost_score",
                "std"
            ),

            provider_count=(
                "rndrng_npi",
                "nunique"
            ),
        )
        .reset_index()
    )

    # Rename year → performance_year
    agg = agg.rename(
        columns={
            "year": "performance_year"
        }
    )

    # --------------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------------

    print(
        f"\nProvider variation:"
        f" {agg.shape}"
    )

    print(
        f"States covered:"
        f" {agg['ACO_State'].nunique()}"
    )

    print(
        "\nProvider states:"
    )

    print(
        sorted(
            agg["ACO_State"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    print(
        "\nProvider variation preview:"
    )

    print(
        agg.to_string(index=False)
    )

    # --------------------------------------------------------
    # COVERAGE
    # --------------------------------------------------------

    print(
        "\nProvider variation coverage:"
    )

    print(
        f"Total provider-selection rows: "
        f"{len(selection)}"
    )

    print(
        f"Rows with known state: "
        f"{known_state}"
    )

    print(
        f"Rows without state: "
        f"{missing_state}"
    )

    return agg


# ============================================================
# 4. READMISSION PROXY
# ============================================================

def load_readmission_proxy():

    print("\n" + "=" * 70)
    print("4. LOADING READMISSION PROXY")
    print("=" * 70)

    """
    There is no true readmission source available
    in the current CMS data.

    Therefore:

        (CHF admissions + COPD admissions) / beneficiaries

    is used as the closest available proxy.

    YoY change is then calculated per ACO.
    """

    df = pd.read_sql(
        text(
            """
            SELECT
                "ACO_ID",
                performance_year,
                "N_AB",
                chf_adm,
                copd_adm

            FROM fact_aco_performance

            ORDER BY
                "ACO_ID",
                performance_year
            """
        ),
        engine
    )

    # Numeric conversion
    df["N_AB"] = pd.to_numeric(
        df["N_AB"],
        errors="coerce"
    )

    df["chf_adm"] = pd.to_numeric(
        df["chf_adm"],
        errors="coerce"
    )

    df["copd_adm"] = pd.to_numeric(
        df["copd_adm"],
        errors="coerce"
    )

    # Avoid division by zero
    denominator = df["N_AB"].replace(
        0,
        np.nan
    )

    # Readmission proxy
    df["readmission_proxy_rate"] = (
        df["chf_adm"].fillna(0)
        +
        df["copd_adm"].fillna(0)
    ) / denominator

    # YoY change
    df["readmission_proxy_rate_yoy_change"] = (
        df
        .groupby("ACO_ID")[
            "readmission_proxy_rate"
        ]
        .diff()
    )

    result = (
        df[
            df["performance_year"] == TARGET_YEAR
        ][
            [
                "ACO_ID",
                "performance_year",
                "readmission_proxy_rate_yoy_change"
            ]
        ]
        .dropna(
            subset=[
                "readmission_proxy_rate_yoy_change"
            ]
        )
    )

    print(
        f"Readmission proxy: {result.shape}"
    )

    print(
        f"ACOs with readmission proxy: "
        f"{result['ACO_ID'].nunique()}"
    )

    return result


# ============================================================
# 5. BUILD FEATURE TABLE
# ============================================================

def build_feature_table():

    print("\n" + "=" * 70)
    print("5. BUILDING FINAL FEATURE TABLE")
    print("=" * 70)

    shared = load_shared_segmentation_features()

    states = load_aco_states()

    provider = load_provider_variation()

    readmission = load_readmission_proxy()

    # --------------------------------------------------------
    # MERGE SHARED FEATURES + ACO STATE
    # --------------------------------------------------------

    merged = shared.merge(
        states,
        on="ACO_ID",
        how="left"
    )

    print("\nAfter ACO state merge:")

    print(
        f"Shape: {merged.shape}"
    )

    print(
        "Missing ACO_State:",
        merged["ACO_State"].isna().sum(),
        "/",
        len(merged)
    )

    # --------------------------------------------------------
    # CHECK STATE COVERAGE
    # --------------------------------------------------------

    missing_states = merged[
        "ACO_State"
    ].isna().sum()

    if missing_states > 0:

        print(
            "\nWARNING:"
        )

        print(
            f"{missing_states} ACOs do not have "
            f"a known historical state."
        )

    # --------------------------------------------------------
    # MERGE PROVIDER VARIATION BY STATE + YEAR
    # --------------------------------------------------------

    merged["ACO_State"] = (
        merged["ACO_State"]
        .astype("string")
    )

    provider["ACO_State"] = (
        provider["ACO_State"]
        .astype("string")
    )

    merged["performance_year"] = pd.to_numeric(
        merged["performance_year"],
        errors="coerce"
    )

    provider["performance_year"] = pd.to_numeric(
        provider["performance_year"],
        errors="coerce"
    )

    # State overlap
    aco_states = set(
        merged["ACO_State"]
        .dropna()
        .tolist()
    )

    provider_states = set(
        provider["ACO_State"]
        .dropna()
        .tolist()
    )

    common_states = (
        aco_states
        .intersection(provider_states)
    )

    print("\nProvider state merge:")

    print(
        f"ACO states: {len(aco_states)}"
    )

    print(
        f"Provider states: {len(provider_states)}"
    )

    print(
        f"Common states: {len(common_states)}"
    )

    print(
        "Common state codes:",
        sorted(common_states)
    )

    merged = merged.merge(
        provider,
        on=[
            "ACO_State",
            "performance_year"
        ],
        how="left"
    )

    # --------------------------------------------------------
    # MERGE READMISSION
    # --------------------------------------------------------

    merged = merged.merge(
        readmission,
        on=[
            "ACO_ID",
            "performance_year"
        ],
        how="left"
    )

    # --------------------------------------------------------
    # FINAL OUTPUT
    # --------------------------------------------------------

    print(
        f"\nFinal merged shape: {merged.shape}"
    )

    print("\nNulls per column after merge:")

    print(
        merged.isnull().sum()
    )

    # --------------------------------------------------------
    # PROVIDER VARIATION COVERAGE
    # --------------------------------------------------------

    provider_nulls = merged[
        [
            "provider_utilization_variation",
            "provider_cost_variation"
        ]
    ].isna().sum()

    print("\nProvider variation missing values:")

    print(provider_nulls)

    print("\nProvider variation coverage:")

    for col in [
        "provider_utilization_variation",
        "provider_cost_variation"
    ]:

        available = merged[col].notna().sum()

        print(
            f"{col}: "
            f"{available}/{len(merged)} "
            f"({available / len(merged) * 100:.2f}%)"
        )

    return merged


# ============================================================
# 6. OUTLIER CHECK
# ============================================================

def plot_outlier_check(
    df,
    feature_cols
):

    print("\n" + "=" * 70)
    print("6. OUTLIER CHECK")
    print("=" * 70)

    valid_cols = []

    for col in feature_cols:

        if col not in df.columns:
            continue

        series = pd.to_numeric(
            df[col],
            errors="coerce"
        )

        if series.notna().sum() > 0:
            valid_cols.append(col)

    if len(valid_cols) == 0:

        print(
            "No valid numeric columns available "
            "for outlier plot."
        )

        return

    n = len(valid_cols)

    fig, axes = plt.subplots(
        1,
        n,
        figsize=(3.5 * n, 4)
    )

    if n == 1:
        axes = [axes]

    for ax, col in zip(
        axes,
        valid_cols
    ):

        series = pd.to_numeric(
            df[col],
            errors="coerce"
        ).dropna()

        sns.boxplot(
            y=series,
            ax=ax
        )

        ax.set_title(
            col,
            fontsize=8
        )

    plt.tight_layout()

    plot_path = (
        f"plots/"
        f"01_outlier_check_{TARGET_YEAR}.png"
    )

    plt.savefig(
        plot_path,
        dpi=150
    )

    plt.close()

    print(
        f"Saved {plot_path}"
    )


# ============================================================
# 7. SAVE FEATURES SAFELY
# ============================================================

def save_features_safely(features):

    print("\n" + "=" * 70)
    print("7. SAVING FEATURES TO SUPABASE")
    print("=" * 70)

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if features.empty:

        raise ValueError(
            "Feature table is empty. "
            "Nothing will be written to the database."
        )

    # Make absolutely sure this feature set is only TARGET_YEAR
    years = (
        features["performance_year"]
        .dropna()
        .unique()
        .tolist()
    )

    print(
        f"Years present in generated features: {years}"
    )

    if len(years) != 1 or int(years[0]) != int(TARGET_YEAR):

        raise ValueError(
            f"Safety check failed. Expected only "
            f"TARGET_YEAR={TARGET_YEAR}, "
            f"but generated years are {years}."
        )

    # --------------------------------------------------------
    # CHECK EXISTING TARGET-YEAR ROWS
    # --------------------------------------------------------

    existing = pd.read_sql(
        text(
            f"""
            SELECT
                performance_year,
                COUNT(*) AS row_count
            FROM {OUTPUT_TABLE}
            WHERE performance_year = :yr
            GROUP BY performance_year
            """
        ),
        engine,
        params={"yr": TARGET_YEAR}
    )

    if existing.empty:

        print(
            f"No existing {TARGET_YEAR} rows found."
        )

    else:

        print(
            f"Existing {TARGET_YEAR} rows:"
        )

        print(existing.to_string(index=False))

    # --------------------------------------------------------
    # DELETE ONLY TARGET YEAR
    # --------------------------------------------------------

    print(
        f"\nDeleting existing {TARGET_YEAR} rows only..."
    )

    with engine.begin() as conn:

        result = conn.execute(
            text(
                f"""
                DELETE FROM {OUTPUT_TABLE}
                WHERE performance_year = :yr
                """
            ),
            {
                "yr": TARGET_YEAR
            }
        )

        print(
            f"Deleted {result.rowcount} existing "
            f"{TARGET_YEAR} rows."
        )

    # --------------------------------------------------------
    # APPEND NEW TARGET YEAR
    # --------------------------------------------------------

    print(
        f"\nAppending {len(features)} new "
        f"{TARGET_YEAR} feature rows..."
    )

    features.to_sql(
        OUTPUT_TABLE,
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    print(
        f"\nSuccessfully saved {len(features)} rows "
        f"for performance_year={TARGET_YEAR}."
    )

    # --------------------------------------------------------
    # VERIFY DATABASE
    # --------------------------------------------------------

    verification = pd.read_sql(
        text(
            f"""
            SELECT
                performance_year,
                COUNT(*) AS row_count,
                COUNT(DISTINCT "ACO_ID") AS unique_acos
            FROM {OUTPUT_TABLE}
            GROUP BY performance_year
            ORDER BY performance_year
            """
        ),
        engine
    )

    print("\nDatabase verification:")

    print(
        verification.to_string(index=False)
    )

    print(
        "\nIMPORTANT:"
    )

    print(
        "Existing years were preserved."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        # ----------------------------------------------------
        # BUILD
        # ----------------------------------------------------

        features = build_feature_table()

        # ----------------------------------------------------
        # FEATURE COLUMNS
        # ----------------------------------------------------

        delta_cols = [
            "savings_yoy_change_pct",
            "expenditure_variance_pct",
            "quality_change_yoy",
            "ed_utilization_change_yoy",
            "admission_change_yoy",
            "em_utilization_change_yoy",
            "advanced_imaging_change_yoy",
            "readmission_proxy_rate_yoy_change",
            "provider_utilization_variation",
            "provider_cost_variation",
        ]

        # ----------------------------------------------------
        # OUTLIER CHECK
        # ----------------------------------------------------

        plot_outlier_check(
            features,
            delta_cols
        )

        # ----------------------------------------------------
        # DESCRIPTIVE STATISTICS
        # ----------------------------------------------------

        print("\n" + "=" * 70)
        print("DESCRIPTIVE STATISTICS")
        print("=" * 70)

        print(
            features[delta_cols].describe()
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        save_features_safely(
            features
        )

        print("\n" + "=" * 70)
        print("BUILD COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:

        print("\n" + "=" * 70)
        print("BUILD FAILED")
        print("=" * 70)

        print(
            f"{type(e).__name__}: {e}"
        )

        raise