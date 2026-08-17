import pandas as pd
from supabase_client import supabase


def load_aco_data(batch_size=1000):
    all_rows = []

    start = 0

    while True:
        end = start + batch_size - 1

        response = (
            supabase
            .table("fact_aco_performance")
            .select("*")
            .range(start, end)
            .execute()
        )

        rows = response.data

        if not rows:
            break

        all_rows.extend(rows)

        print(f"Loaded {len(all_rows)} rows")

        if len(rows) < batch_size:
            break

        start += batch_size

    df = pd.DataFrame(all_rows)

    print("Final shape:", df.shape)

    return df
if __name__ == "__main__":
    df = load_aco_data()
    print(df.head())