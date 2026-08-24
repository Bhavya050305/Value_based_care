"""Tests for health check endpoints and core API foundation middleware/handlers."""

from fastapi.testclient import TestClient


def test_health_check_endpoint(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["status"] == "ok"
    assert "version" in data["data"]
    assert "environment" in data["data"]
    assert "meta" in data
    assert "request_id" in data["meta"]
    assert "X-Request-ID" in response.headers


def test_readiness_check_endpoint(client: TestClient):
    response = client.get("/api/v1/health/ready")
    # Without configured DB and Redis, readiness is not_ready with 503
    assert response.status_code in (200, 503)

    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "status" in data["data"]
    assert "checks" in data["data"]
    assert "database" in data["data"]["checks"]
    assert "redis" in data["data"]["checks"]


def test_not_found_error_envelope(client: TestClient):
    response = client.get("/api/v1/nonexistent-route-for-testing")
    assert response.status_code == 404

    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "request_id" in data["error"]
