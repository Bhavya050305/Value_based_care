import os
from collections import Counter
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

print("=" * 60)
print("DUPLICATE + YEAR VALIDATION")
print("=" * 60)

# ---------------------------------------------------------
# Fetch relevant columns
# ---------------------------------------------------------

all_rows = []

page_size = 1000
total_rows = 150000
start = 0

columns = (
    "Rndrng_NPI,"
    "Rndrng_Prvdr_Type,"
    "Rndrng_Prvdr_State_Abrvtn,"
    "Tot_HCPCS_Cds,"
    "Tot_Benes,"
    "Tot_Srvcs,"
    "Tot_Mdcr_Alowd_Amt,"
    "Tot_Mdcr_Pymt_Amt,"
    "Tot_Mdcr_Stdzd_Amt,"
    "Year"
)

while start < total_rows:

    end = min(start + page_size - 1, total_rows - 1)

    response = (
    client
    .table("provider_combined")
    .select(columns)
    .order("Rndrng_NPI")
    .order("Year")
    .order("Rndrng_Prvdr_Type")
    .order("Rndrng_Prvdr_State_Abrvtn")
    .order("Tot_HCPCS_Cds")
    .order("Tot_Benes")
    .order("Tot_Srvcs")
    .order("Tot_Mdcr_Alowd_Amt")
    .order("Tot_Mdcr_Pymt_Amt")
    .order("Tot_Mdcr_Stdzd_Amt")
    .range(start, end)
    .execute()
)

    all_rows.extend(response.data)

    start += page_size

    if start % 10000 == 0:
        print("Fetched:", len(all_rows))


# ---------------------------------------------------------
# Year distribution
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("YEAR DISTRIBUTION")
print("=" * 60)

year_counts = Counter(
    row["Year"]
    for row in all_rows
)

for year, count in sorted(
    year_counts.items(),
    key=lambda x: str(x[0])
):
    print(f"{year}: {count} rows")


# ---------------------------------------------------------
# NPI-Year combinations
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("NPI-YEAR GRAIN")
print("=" * 60)

npi_year_counts = Counter(
    (
        row["Rndrng_NPI"],
        row["Year"]
    )
    for row in all_rows
)

print("Unique NPI-Year combinations:", len(npi_year_counts))

duplicate_npi_years = {
    key: count
    for key, count in npi_year_counts.items()
    if count > 1
}

print(
    "Repeated NPI-Year combinations:",
    len(duplicate_npi_years)
)

print("\nTop repeated NPI-Year combinations:")

for key, count in sorted(
    duplicate_npi_years.items(),
    key=lambda x: x[1],
    reverse=True
)[:10]:

    print(
        f"NPI={key[0]}, Year={key[1]} → {count} rows"
    )


# ---------------------------------------------------------
# Exact duplicate detection
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("EXACT DUPLICATE VALIDATION")
print("=" * 60)

row_keys = []

for row in all_rows:

    key = tuple(
        row.get(column)
        for column in [
            "Rndrng_NPI",
            "Rndrng_Prvdr_Type",
            "Rndrng_Prvdr_State_Abrvtn",
            "Tot_HCPCS_Cds",
            "Tot_Benes",
            "Tot_Srvcs",
            "Tot_Mdcr_Alowd_Amt",
            "Tot_Mdcr_Pymt_Amt",
            "Tot_Mdcr_Stdzd_Amt",
            "Year"
        ]
    )

    row_keys.append(key)

unique_rows = set(row_keys)

print("Total rows:", len(row_keys))
print("Unique rows:", len(unique_rows))
print(
    "Duplicate occurrences:",
    len(row_keys) - len(unique_rows)
)

print("\n" + "=" * 60)
print("DUPLICATE + YEAR VALIDATION COMPLETE")
print("=" * 60)