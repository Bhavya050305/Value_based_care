import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("=" * 60)
print("SUPABASE CONNECTION CHECK")
print("=" * 60)

print("SUPABASE_URL present:", bool(SUPABASE_URL))
print("SERVICE_ROLE_KEY present:", bool(SUPABASE_SERVICE_ROLE_KEY))

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError(
        "Supabase credentials are missing from the .env file."
    )

# Create Supabase client
client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY
)

print("Supabase client created successfully.")

# ---------------------------------------------------------
# Check provider_combined
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("TABLE: provider_combined")
print("=" * 60)

provider_response = (
    client
    .table("provider_combined")
    .select("*")
    .limit(5)
    .execute()
)

provider_rows = provider_response.data

print("Rows returned:", len(provider_rows))

if provider_rows:
    print("\nColumns:")
    for column in provider_rows[0].keys():
        print(" -", column)

# ---------------------------------------------------------
# Check provider_service_lookup
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("TABLE: provider_service_lookup")
print("=" * 60)

service_response = (
    client
    .table("provider_service_lookup")
    .select("*")
    .limit(5)
    .execute()
)

service_rows = service_response.data

print("Rows returned:", len(service_rows))

if service_rows:
    print("\nColumns:")
    for column in service_rows[0].keys():
        print(" -", column)

print("\n" + "=" * 60)
print("VALIDATION STEP COMPLETE")
print("=" * 60)
# ---------------------------------------------------------
# Provider Combined: Basic Statistics
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("PROVIDER_COMBINED STATISTICS")
print("=" * 60)

# Total rows
count_response = (
    client
    .table("provider_combined")
    .select("Rndrng_NPI", count="exact")
    .limit(1)
    .execute()
)

print("Total rows:", count_response.count)

# Unique NPIs
npi_response = (
    client
    .table("provider_combined")
    .select("Rndrng_NPI")
    .execute()
)

provider_npis = [
    row["Rndrng_NPI"]
    for row in npi_response.data
    if row["Rndrng_NPI"] is not None
]

print("Non-null NPI rows:", len(provider_npis))
print("Unique NPIs:", len(set(provider_npis)))
print("Null NPIs:", len(npi_response.data) - len(provider_npis))

# Duplicate NPI count
duplicate_npis = len(provider_npis) - len(set(provider_npis))

print("Duplicate NPI occurrences:", duplicate_npis)

# ---------------------------------------------------------
# Year validation
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("YEAR VALIDATION")
print("=" * 60)

year_response = (
    client
    .table("provider_combined")
    .select("Year, performance_year")
    .execute()
)

years = sorted(
    set(
        str(row["Year"])
        for row in year_response.data
        if row["Year"] is not None
    )
)

performance_years = sorted(
    set(
        str(row["performance_year"])
        for row in year_response.data
        if row["performance_year"] is not None
    )
)

print("Year values:", years)
print("Performance year values:", performance_years)

# ---------------------------------------------------------
# Provider Service Lookup statistics
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("PROVIDER_SERVICE_LOOKUP STATISTICS")
print("=" * 60)

service_count_response = (
    client
    .table("provider_service_lookup")
    .select("Rndrng_NPI", count="exact")
    .limit(1)
    .execute()
)

print("Total rows:", service_count_response.count)

service_npi_response = (
    client
    .table("provider_service_lookup")
    .select("Rndrng_NPI")
    .execute()
)

service_npis = [
    row["Rndrng_NPI"]
    for row in service_npi_response.data
    if row["Rndrng_NPI"] is not None
]

print("Non-null NPI rows:", len(service_npis))
print("Unique NPIs:", len(set(service_npis)))
print("Null NPIs:", len(service_npi_response.data) - len(service_npis))

print("\n" + "=" * 60)
print("STATISTICS VALIDATION COMPLETE")
print("=" * 60)
# ---------------------------------------------------------
# Inspect actual provider_combined rows
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("SAMPLE PROVIDER_COMBINED ROWS")
print("=" * 60)

sample_provider_response = (
    client
    .table("provider_combined")
    .select("*")
    .limit(10)
    .execute()
)

for i, row in enumerate(sample_provider_response.data, start=1):
    print(f"\n--- Provider row {i} ---")
    print(row)


# ---------------------------------------------------------
# Inspect actual provider_service_lookup rows
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("SAMPLE PROVIDER_SERVICE_LOOKUP ROWS")
print("=" * 60)

sample_service_response = (
    client
    .table("provider_service_lookup")
    .select("*")
    .limit(10)
    .execute()
)

for i, row in enumerate(sample_service_response.data, start=1):
    print(f"\n--- Service lookup row {i} ---")
    print(row)