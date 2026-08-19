"""Tests for Supabase Auth JWT validation, RBAC dependencies, and /auth/me endpoint."""

from jose import jwt
from fastapi.testclient import TestClient

from app.core.config import get_settings


def test_auth_me_unauthorized_without_token(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTHENTICATION_ERROR"


def test_auth_me_with_jwt_token(client: TestClient):
    settings = get_settings()

    payload = {
        "sub": "user_123456",
        "email": "executive@example.com",
        "app_metadata": {
            "role": "executive",
            "organization_id": "org_789",
        },
        "amr": [{"method": "mfa"}],
    }

    secret = settings.supabase_jwt_secret or "test_secret_for_jwt_validation"
    # Temporarily set secret if not set for test runtime
    original_secret = settings.supabase_jwt_secret
    settings.supabase_jwt_secret = secret

    try:
        token = jwt.encode(payload, secret, algorithm="HS256")
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["user_id"] == "user_123456"
        assert data["data"]["email"] == "executive@example.com"
        assert data["data"]["role"] == "executive"
        assert data["data"]["organization_id"] == "org_789"
        assert "read:portfolio" in data["data"]["permissions"]
        assert data["data"]["mfa_verified"] is True
    finally:
        settings.supabase_jwt_secret = original_secret
