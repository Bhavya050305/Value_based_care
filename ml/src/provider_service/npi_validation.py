import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

print("=" * 60)
print("ACCURATE NPI VALIDATION")
print("=" * 60)

# Supabase exact row count
count_response = (
    client
    .table("provider_combined")
    .select("Rndrng_NPI", count="exact")
    .limit(1)
    .execute()
)

total_rows = count_response.count

print("Total rows:", total_rows)

# Fetch all NPIs in pages
all_npis = []

page_size = 1000
start = 0

while start < total_rows:

    end = min(start + page_size - 1, total_rows - 1)

    response = (
        client
        .table("provider_combined")
        .select("Rndrng_NPI")
        .range(start, end)
        .execute()
    )

    rows = response.data

    all_npis.extend(
        row["Rndrng_NPI"]
        for row in rows
    )

    start += page_size

    print("Fetched:", len(all_npis))

# Statistics
non_null_npis = [
    npi for npi in all_npis
    if npi is not None
]

unique_npis = set(non_null_npis)

print()
print("=" * 60)
print("FINAL NPI STATISTICS")
print("=" * 60)

print("Total rows:", len(all_npis))
print("Non-null NPIs:", len(non_null_npis))
print("Unique NPIs:", len(unique_npis))
print("Null NPIs:", len(all_npis) - len(non_null_npis))
print(
    "Duplicate NPI occurrences:",
    len(non_null_npis) - len(unique_npis)
)

print("=" * 60)
print("NPI VALIDATION COMPLETE")
print("=" * 60)