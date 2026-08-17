from supabase_client import supabase

response = (
    supabase
    .table("fact_aco_performance")
    .select("ACO_ID, ACO_Name, performance_year, QualScore, Sav_rate")
    .limit(10)
    .execute()
)

print("Rows received:", len(response.data))

for row in response.data:
    print(row)