"""Integration tests for all VBC Command Center API v1 endpoints."""

from jose import jwt
from fastapi.testclient import TestClient

from app.core.config import get_settings


def _get_auth_headers(role: str = "executive") -> dict[str, str]:
    settings = get_settings()
    secret = settings.supabase_jwt_secret or "test_secret"
    settings.supabase_jwt_secret = secret

    payload = {
        "sub": "user_test_999",
        "email": "test@vbc-command.org",
        "app_metadata": {
            "role": role,
            "organization_id": "org_test",
        },
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


def test_portfolio_endpoints(client: TestClient):
    headers = _get_auth_headers("executive")

    # Missing year parameter -> 422 Unprocessable Entity
    res_missing = client.get("/api/v1/portfolio/summary", headers=headers)
    assert res_missing.status_code == 422

    res = client.get("/api/v1/portfolio/summary?year=2024", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["total_acos"] >= 12

    res = client.get("/api/v1/portfolio/risk-distribution?year=2024", headers=headers)
    assert res.status_code == 200

    res = client.get("/api/v1/portfolio/trends", headers=headers)
    assert res.status_code == 200

    res = client.get("/api/v1/portfolio/acos?year=2024", headers=headers)
    assert res.status_code == 200


def test_aco_explorer_endpoints(client: TestClient):
    headers = _get_auth_headers("executive")

    # Missing year parameter -> 422 Unprocessable Entity
    res_missing = client.get("/api/v1/acos", headers=headers)
    assert res_missing.status_code == 422

    res = client.get("/api/v1/acos?year=2024", headers=headers)
    assert res.status_code == 200
    assert len(res.json()["data"]) > 0

    res = client.get("/api/v1/acos/A1001?year=2024", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["aco_id"] == "A1001"


def test_performance_endpoints(client: TestClient):
    headers = _get_auth_headers("executive")

    res = client.get("/api/v1/acos/A1001/summary?year=2024", headers=headers)
    assert res.status_code == 200

    res = client.get("/api/v1/acos/A1001/financial?year=2024", headers=headers)
    assert res.status_code == 200

    res = client.get("/api/v1/acos/A1001/quality?year=2024", headers=headers)
    assert res.status_code == 200

    res = client.get("/api/v1/acos/A1001/utilization?year=2024", headers=headers)
    assert res.status_code == 200


def test_trends_and_drivers(client: TestClient):
    headers = _get_auth_headers("executive")

    res = client.get("/api/v1/acos/A1001/trends", headers=headers)
    assert res.status_code == 200

    res = client.get("/api/v1/acos/A1001/drivers", headers=headers)
    assert res.status_code == 200

    res = client.get("/api/v1/predictions/A1001", headers=headers)
    assert res.status_code == 200


def test_simulator_and_recommendations(client: TestClient):
    headers = _get_auth_headers("executive")

    sim_payload = {
        "aco_id": "A1001",
        "target_year": 2025,
        "quality_score_delta": 2.0,
        "utilization_change_pct": -3.0,
    }
    res = client.post("/api/v1/simulations", json=sim_payload, headers=headers)
    assert res.status_code == 200
    assert "expenditure_impact" in res.json()["data"]

    res = client.get("/api/v1/recommendations", headers=headers)
    assert res.status_code == 200

    res = client.post("/api/v1/recommendations/rec_101/accept", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "accepted"


def test_new_ten_endpoints(client: TestClient):
    headers = _get_auth_headers("executive")

    # 1. GET /api/v1/predictions/{prediction_id}/explanation
    res = client.get("/api/v1/predictions/pred_A1001_2024/explanation", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["prediction_id"] == "pred_A1001_2024"
    assert "top_drivers" in res.json()["data"]

    # 2. Run simulation & GET /api/v1/simulations/{simulation_id}
    sim_res = client.post(
        "/api/v1/simulations",
        json={"aco_id": "A1001", "target_year": 2025, "utilization_change_pct": -2.5},
        headers=headers,
    )
    assert sim_res.status_code == 200
    sim_id = sim_res.json()["data"]["simulation_id"]

    res = client.get(f"/api/v1/simulations/{sim_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["simulation_id"] == sim_id

    # 3. GET /api/v1/acos/{aco_id}/simulations
    res = client.get("/api/v1/acos/A1001/simulations", headers=headers)
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    # 4. GET /api/v1/actions/{action_id}
    res = client.get("/api/v1/actions/act_501", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["id"] == "act_501"

    # 5. PATCH /api/v1/actions/{action_id}
    res = client.patch(
        "/api/v1/actions/act_501",
        json={"assigned_to": "Medical Director"},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["data"]["assigned_to"] == "Medical Director"

    # 6. POST /api/v1/actions/{action_id}/outcomes
    out_payload = {
        "metric_name": "ED Visit Rate per 1k",
        "pre_action_value": 410.2,
        "post_action_value": 385.0,
    }
    res = client.post("/api/v1/actions/act_501/outcomes", json=out_payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["action_id"] == "act_501"
    out_id = res.json()["data"]["id"]

    # 7. GET /api/v1/actions/{action_id}/outcomes/{outcome_id}
    res = client.get(f"/api/v1/actions/act_501/outcomes/{out_id}", headers=headers)
    assert res.status_code == 200

    # 8. GET /api/v1/reports/{report_id}
    res = client.get("/api/v1/reports/rep_101", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["id"] == "rep_101"

    # 9. PATCH /api/v1/settings/profile
    res = client.patch(
        "/api/v1/settings/profile",
        json={"full_name": "Chief Medical Officer"},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["data"]["full_name"] == "Chief Medical Officer"

    # 10. PATCH /api/v1/settings/preferences
    res = client.patch(
        "/api/v1/settings/preferences",
        json={"theme": "light", "default_performance_year": 2025},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["data"]["theme"] == "light"
