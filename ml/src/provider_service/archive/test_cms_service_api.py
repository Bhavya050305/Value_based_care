import requests
import json

API_URL = "https://data.cms.gov/data-api/v1/dataset/0e9f2f2b-7bf9-451a-912c-e02e654dd725/data"

TEST_NPI = "1609082486"

params = {
    "filter[Rndrng_NPI]": TEST_NPI,
    "column": (
        "Rndrng_NPI,"
        "Rndrng_Prvdr_Last_Org_Name,"
        "Rndrng_Prvdr_First_Name,"
        "HCPCS_Cd,"
        "HCPCS_Desc,"
        "Place_Of_Srvc,"
        "Tot_Benes,"
        "Tot_Srvcs,"
        "Avg_Sbmtd_Chrg,"
        "Avg_Mdcr_Alowd_Amt,"
        "Avg_Mdcr_Pymt_Amt,"
        "Avg_Mdcr_Stdzd_Amt"
    ),
    "size": "10",
    "offset": "0"
}

print("=" * 70)
print("CMS PROVIDER + SERVICE API TEST")
print("=" * 70)

print()
print("Testing NPI:", TEST_NPI)
print("Sending request to CMS...")

try:
    response = requests.get(
        API_URL,
        params=params,
        timeout=(15, 180)
    )

    print()
    print("HTTP STATUS:", response.status_code)
    print("FINAL URL:")
    print(response.url)

    response.raise_for_status()

    data = response.json()

    print()
    print("RESPONSE TYPE:", type(data).__name__)

    if isinstance(data, list):
        print("NUMBER OF RECORDS:", len(data))

        if len(data) > 0:
            print()
            print("FIRST RECORD:")
            print(json.dumps(data[0], indent=2))

        print()
        print("=" * 70)
        print("API TEST PASSED")
        print("=" * 70)

    else:
        print()
        print("UNEXPECTED RESPONSE:")
        print(json.dumps(data, indent=2)[:5000])

except requests.exceptions.Timeout:
    print()
    print("=" * 70)
    print("CMS API TIMED OUT")
    print("=" * 70)
    print()
    print("CMS did not respond within 180 seconds.")

except requests.exceptions.RequestException as e:
    print()
    print("=" * 70)
    print("CMS API REQUEST FAILED")
    print("=" * 70)
    print()
    print(str(e))