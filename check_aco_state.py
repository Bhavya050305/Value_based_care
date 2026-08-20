import pandas as pd
from sqlalchemy import text
from db import engine, TARGET_YEAR

print("=" * 70)
print("FINDING ACO -> STATE MAPPING")
print("=" * 70)

# 1. Check whether segmentation table already has state
print("\n1. aco_segmentation_ml_features columns")

query = text("""
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'aco_segmentation_ml_features'
ORDER BY ordinal_position
""")

with engine.connect() as conn:
    df = pd.read_sql(query, conn)

print(df.to_string(index=False))


# 2. Find all tables containing both ACO and STATE columns
print("\n2. Tables containing both ACO and STATE")

query = text("""
SELECT
    a.table_name
FROM information_schema.columns a
JOIN information_schema.columns s
    ON a.table_schema = s.table_schema
   AND a.table_name = s.table_name
WHERE a.table_schema = 'public'
  AND LOWER(a.column_name) LIKE '%aco%'
  AND LOWER(s.column_name) LIKE '%state%'
GROUP BY a.table_name
ORDER BY a.table_name
""")

with engine.connect() as conn:
    tables = pd.read_sql(query, conn)

print(tables.to_string(index=False))