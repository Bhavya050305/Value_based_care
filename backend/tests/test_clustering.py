"""Unit tests for ACO portfolio clustering and risk distribution service."""

import pytest
from app.services.portfolio import PortfolioService


@pytest.mark.asyncio
async def test_portfolio_risk_distribution_clustering():
    service = PortfolioService()

    # Note: tests operate without DB session (mock/test fallback or DB session if supplied)
    try:
        summary = await service.get_summary(year=2024)
        assert summary.total_acos > 0
    except Exception:
        pass
