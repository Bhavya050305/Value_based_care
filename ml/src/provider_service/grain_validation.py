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
print("PROVIDER_COMBINED GRAIN VALIDATION")
print("=" * 60)

# Fetch the important columns only
all_rows = []

page_size = 1000
total_rows = 150000
start = 0

while start < total_rows:

    end = min(start + page_size - 1, total_rows - 1)

    response = (
        client
        .table("provider_combined")
        .select(
            "Rndrng_NPI,"
            "Rndrng_Prvdr_Type,"
            "Rndrng_Prvdr_State_Abrvtn,"
            "Tot_HCPCS_Cds,"
            "Tot_Benes,"
            "Tot_Srvcs,"
            "Year,"
            "provider_name,"
            "performance_year"
        )
        .range(start, end)
        .execute()
    )

    all_rows.extend(response.data)

    start += page_size

    print("Fetched:", len(all_rows))

# ---------------------------------------------------------
# NPI frequency
# ---------------------------------------------------------

npi_counts = Counter(
    row["Rndrng_NPI"]
    for row in all_rows
)

repeated = {
    npi: count
    for npi, count in npi_counts.items()
    if count > 1
}

print("\n" + "=" * 60)
print("NPI FREQUENCY")
print("=" * 60)

print("Unique NPIs:", len(npi_counts))
print("Repeated NPIs:", len(repeated))
print("Maximum rows for one NPI:", max(npi_counts.values()))

# Show top repeated NPIs
print("\nTop 10 repeated NPIs:")

for npi, count in sorted(
    repeated.items(),
    key=lambda x: x[1],
    reverse=True
)[:10]:

    print(f"  {npi}: {count} rows")


# ---------------------------------------------------------
# Inspect one repeated NPI
# ---------------------------------------------------------

if repeated:

    test_npi = next(iter(repeated))

    test_rows = [
        row
        for row in all_rows
        if row["Rndrng_NPI"] == test_npi
    ]

    print("\n" + "=" * 60)
    print("REPEATED NPI SAMPLE")
    print("=" * 60)

    print("NPI:", test_npi)
    print("Rows:", len(test_rows))

    for i, row in enumerate(test_rows[:10], start=1):

        print(f"\n--- Row {i} ---")

        print("Provider Type:", row["Rndrng_Prvdr_Type"])
        print("State:", row["Rndrng_Prvdr_State_Abrvtn"])
        print("HCPCS Codes:", row["Tot_HCPCS_Cds"])
        print("Beneficiaries:", row["Tot_Benes"])
        print("Services:", row["Tot_Srvcs"])
        print("Year:", row["Year"])
        print("Provider Name:", row["provider_name"])
        print("Performance Year:", row["performance_year"])


print("\n" + "=" * 60)
print("GRAIN VALIDATION COMPLETE")
print("=" * 60)