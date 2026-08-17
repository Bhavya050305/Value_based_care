import joblib
import pandas as pd

from load_data import load_aco_data
from peer_model import prepare_reference


MODEL_PATH = "ml/models/peer_target_finder/model.pkl"


print("==========================================")
print("MULTI-YEAR PEER TARGET FINDER TEST")
print("==========================================")

print()
print("Loading trained model...")

model = joblib.load(MODEL_PATH)

print("Model loaded successfully.")

print()
print("Loading data from Supabase...")

df = load_aco_data()

print()
print("Preparing data...")

reference = prepare_reference(df)

print()
print("Dataset shape:", reference.shape)


# ============================================================
# FIND AN ACO WITH THE MOST AVAILABLE YEARS
# ============================================================

year_counts = (
    reference
    .groupby("ACO_ID")["performance_year"]
    .nunique()
    .sort_values(ascending=False)
)

# Pick an ACO with the largest number of years
test_aco_id = year_counts.index[0]

available_years = sorted(
    reference[
        reference["ACO_ID"].astype(str)
        == str(test_aco_id)
    ]["performance_year"]
    .unique()
)


print()
print("==========================================")
print("ACO SELECTED FOR MULTI-YEAR TEST")
print("==========================================")

print()
print("ACO ID:", test_aco_id)

aco_rows = reference[
    reference["ACO_ID"].astype(str)
    == str(test_aco_id)
]

print(
    "ACO Name:",
    aco_rows.iloc[0]["ACO_Name"]
)

print(
    "Available years:",
    available_years
)


# ============================================================
# TEST EVERY AVAILABLE YEAR
# ============================================================

print()
print("==========================================")
print("RUNNING YEAR-BY-YEAR TEST")
print("==========================================")


all_passed = True


for year in available_years:

    print()
    print("------------------------------------------")
    print(f"Testing {test_aco_id} - {year}")
    print("------------------------------------------")

    try:

        result = model.predict(
            test_aco_id,
            int(year),
            top_k=3
        )

        print()
        print("Target year:")
        print(
            result["target_aco"]["performance_year"]
        )

        print()
        print("Target performance:")

        print(
            "Savings:",
            result["target_aco"]["savings_pct"],
            "%"
        )

        print(
            "Quality:",
            result["target_aco"]["quality"]
        )

        print(
            "PMPM: $",
            round(
                result["target_aco"]["pmpm"],
                2
            )
        )

        print()
        print("Selected peers:")

        peers = result["similar_peers"]

        if len(peers) == 0:

            print("No peers found.")

            all_passed = False

        else:

            for peer in peers:

                peer_id = peer["ACO_ID"]

                print(
                    f"- {peer_id} | "
                    f"Savings: "
                    f"{peer['savings_pct']}% | "
                    f"Quality: "
                    f"{peer['quality']} | "
                    f"PMPM: "
                    f"${peer['pmpm']:.2f}"
                )

        # ----------------------------------------------------
        # VERIFY TARGET IS NOT ITS OWN PEER
        # ----------------------------------------------------

        target_found_as_peer = any(
            str(peer["ACO_ID"])
            == str(test_aco_id)
            for peer in peers
        )

        if target_found_as_peer:

            print()
            print(
                "❌ FAIL: Target ACO appeared "
                "as its own peer."
            )

            all_passed = False

        else:

            print()
            print(
                "✅ Target ACO correctly excluded "
                "from peer list."
            )

        # ----------------------------------------------------
        # CHECK CLASSIFICATION
        # ----------------------------------------------------

        print()
        print(
            "Classification:",
            result["classification"]
        )

        print()
        print(
            "Benchmark source:",
            result["benchmark_source"]
        )

        print()
        print(
            "Recommendation:",
            result["recommendation"]
        )

    except Exception as e:

        print()
        print(
            f"❌ ERROR testing year {year}:"
        )

        print(e)

        all_passed = False


# ============================================================
# FINAL RESULT
# ============================================================

print()
print()
print("==========================================")
print("MULTI-YEAR TEST RESULT")
print("==========================================")

if all_passed:

    print()
    print(
        "✅ MULTI-YEAR TEST PASSED"
    )

    print()
    print(
        "The model successfully handled "
        "all available years for the selected ACO."
    )

    print()
    print(
        "The target ACO was excluded from "
        "its own peer list for every year."
    )

else:

    print()
    print(
        "❌ MULTI-YEAR TEST NEEDS REVIEW"
    )