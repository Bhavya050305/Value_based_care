import joblib
import pandas as pd

from load_data import load_aco_data
from peer_model import prepare_reference


MODEL_PATH = "ml/models/peer_target_finder/model.pkl"


print("Loading trained Peer Target Finder model...")

model = joblib.load(MODEL_PATH)

print("Loading data from Supabase...")

df = load_aco_data()

print("Preparing data...")

reference = prepare_reference(df)


# ============================================================
# FIND POTENTIAL HIGH-PERFORMING ACOS
# ============================================================

# Calculate percentile ranks.
# Higher savings = better
# Higher quality = better
# Lower PMPM = better

reference["savings_rank"] = (
    reference["SavingsPct"]
    .rank(pct=True)
)

reference["quality_rank"] = (
    reference["QualScore"]
    .rank(pct=True)
)

reference["pmpm_rank"] = (
    1 - reference["PMPM"]
    .rank(pct=True)
)


# Overall performance score
reference["performance_score"] = (
    reference["savings_rank"]
    + reference["quality_rank"]
    + reference["pmpm_rank"]
)


# Sort strongest candidates first
candidates = (
    reference
    .sort_values(
        "performance_score",
        ascending=False
    )
    .drop_duplicates(
        subset=["ACO_ID", "performance_year"]
    )
    .head(30)
)


print()
print("Testing potential high performers...")
print()


# ============================================================
# TEST CANDIDATES
# ============================================================

found = False

for _, row in candidates.iterrows():

    aco_id = str(row["ACO_ID"])
    year = int(row["performance_year"])

    try:

        result = model.predict(
            aco_id,
            year,
            top_k=3
        )

        if result["classification"] == "High Performer":

            print("==========================================")
            print("HIGH PERFORMER FOUND")
            print("==========================================")

            print()
            print("ACO ID:")
            print(aco_id)

            print()
            print("ACO Name:")
            print(row["ACO_Name"])

            print()
            print("Performance Year:")
            print(year)

            print()
            print("Current Performance:")
            print(
                f"Savings : "
                f"{result['target_aco']['savings_pct']}%"
            )

            print(
                f"Quality : "
                f"{result['target_aco']['quality']}"
            )

            print(
                f"PMPM    : "
                f"${result['target_aco']['pmpm']:.2f}"
            )

            print()
            print("Benchmark:")
            print(
                f"Savings : "
                f"{result['benchmark']['savings_pct']}%"
            )

            print(
                f"Quality : "
                f"{result['benchmark']['quality']}"
            )

            print(
                f"PMPM    : "
                f"${result['benchmark']['pmpm']:.2f}"
            )

            print()
            print("Classification:")
            print(
                result["classification"]
            )

            print()
            print("Recommendation:")
            print(
                result["recommendation"]
            )

            print()
            print("Benchmark Source:")
            print(
                result["benchmark_source"]
            )

            print()
            print("Similar Peers:")

            for peer in result["similar_peers"]:

                print(
                    f"- {peer['ACO_ID']} | "
                    f"Savings: {peer['savings_pct']}% | "
                    f"Quality: {peer['quality']} | "
                    f"PMPM: ${peer['pmpm']:.2f}"
                )

            print()
            print("==========================================")

            found = True

            break

    except Exception as e:

        print(
            f"Could not test {aco_id} "
            f"({year}): {e}"
        )


# ============================================================
# IF NO HIGH PERFORMER WAS FOUND
# ============================================================

if not found:

    print()
    print("==========================================")
    print("NO HIGH PERFORMER FOUND IN TOP CANDIDATES")
    print("==========================================")
    print()
    print(
        "This does NOT mean the model is wrong."
    )
    print(
        "It means the tested candidates still "
        "had similar peers that performed better."
    )