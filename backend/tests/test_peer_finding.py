import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

AUTH_HEADERS = {"Authorization": "Bearer dev_demo_token"}

@pytest.mark.asyncio
async def test_find_peers_post_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/peer-target/find-peers",
            headers=AUTH_HEADERS,
            json={"aco_id": "A1001", "performance_year": 2024, "limit": 5, "offset": 0}
        )
        assert res.status_code == 200
        data = res.json()
        assert data["aco_id"] == "A1001"
        assert data["performance_year"] == 2024
        assert "peers" in data
        assert len(data["peers"]) <= 5
        assert data["total"] > 0
        assert data["has_more"] is True

@pytest.mark.asyncio
async def test_find_peers_pagination():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res1 = await ac.post(
            "/api/v1/peer-target/find-peers",
            headers=AUTH_HEADERS,
            json={"aco_id": "A1001", "performance_year": 2024, "limit": 5, "offset": 0}
        )
        res2 = await ac.post(
            "/api/v1/peer-target/find-peers",
            headers=AUTH_HEADERS,
            json={"aco_id": "A1001", "performance_year": 2024, "limit": 5, "offset": 5}
        )
        assert res1.status_code == 200
        assert res2.status_code == 200
        data1 = res1.json()
        data2 = res2.json()
        assert data1["peers"][0]["rank"] == 1
        assert data2["peers"][0]["rank"] == 6
        assert data1["peers"][0]["aco_id"] != data2["peers"][0]["aco_id"]

@pytest.mark.asyncio
async def test_acos_explorer_year_validation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Valid year
        res_valid = await ac.get("/api/v1/acos?year=2024", headers=AUTH_HEADERS)
        assert res_valid.status_code == 200
        assert len(res_valid.json()["data"]) > 0

        # Missing year parameter -> should fail with 422
        res_invalid = await ac.get("/api/v1/acos", headers=AUTH_HEADERS)
        assert res_invalid.status_code == 422
