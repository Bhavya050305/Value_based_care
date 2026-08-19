import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

def _get_auth_headers():
    from jose import jwt
    from app.core.config import get_settings
    settings = get_settings()
    secret = settings.supabase_jwt_secret or "test_secret_for_jwt_validation"
    payload = {
        "sub": "test-user-id",
        "email": "executive@example.com",
        "role": "executive",
        "organization_id": "org_test",
        "aud": "authenticated",
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_health_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/health")
        assert res.status_code == 200
        data = res.json()
        assert data["data"]["status"] == "ok"

@pytest.mark.asyncio
async def test_models_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/health/models")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["models"]["financial_model"] == "loaded"

@pytest.mark.asyncio
async def test_real_aco_summary_endpoint():
    headers = _get_auth_headers()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/acos/A1001/summary?year=2024", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["data"]["aco_id"] == "A1001"

@pytest.mark.asyncio
async def test_real_aco_performance_endpoint():
    headers = _get_auth_headers()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/acos/A1001/financial?year=2024", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["data"]["aco_id"] == "A1001"

@pytest.mark.asyncio
async def test_realtime_report_endpoint():
    headers = _get_auth_headers()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/acos/A1001/report?performance_year=2023", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["aco_id"] == "A1001"
        assert "narrative" in data
        assert "data" in data

