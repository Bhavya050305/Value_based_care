import requests
import pandas as pd

DATASET_ID = "d33cf946-28cd-4479-b55e-73024331f4ca"

url = f"https://data.cms.gov/data-api/v1/dataset/{DATASET_ID}/data"

params = {
    "size": 10,
    "offset": 0
}

print("Testing CMS MSSP API...")

try:
    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    print("HTTP Status:", response.status_code)

    response.raise_for_status()

    data = response.json()

    df = pd.DataFrame(data)

    print("\nSUCCESS!")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head())

except Exception as e:
    print("\nAPI TEST FAILED:")
    print(e)