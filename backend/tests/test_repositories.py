"""Tests for ORM model declarations and base repository queries."""

from app.models.domain import (
    ACO,
    ACOFinancialMLTraining,
    Organization,
    UserProfile,
)
from app.repositories.base import BaseRepository


def test_orm_model_instantiation():
    org = Organization(
        name="Health ACO Network",
        slug="health-aco-network",
    )

    assert org.name == "Health ACO Network"
    assert org.slug == "health-aco-network"

    aco = ACO(
        aco_id="A1001",
        name="Test ACO Alpha",
        state="FL",
        track="Enhanced",
        organization_id="org_123",
    )

    assert aco.aco_id == "A1001"
    assert aco.state == "FL"
    assert aco.organization_id == "org_123"


def test_user_profile_model():
    user = UserProfile(
        id="user_999",
        email="analyst@example.com",
        full_name="Jane Doe",
        role="analyst",
        organization_id="org_123",
    )

    assert user.id == "user_999"
    assert user.role == "analyst"
    assert user.organization_id == "org_123"


def test_aco_financial_ml_training_model():
    financial = ACOFinancialMLTraining(
        aco_id="A1001",
        feature_year=2023,
        target_year=2024,
        benchmark_expenditure=1098668352,
        actual_expenditure=998768668,
        gross_savings_loss=99899684,
        earned_shared_savings=73426268,
        final_share_rate=75,
        final_loss_rate=40,
        savings_loss_pct=9.09279709551513,
        expenditure_variance_pct=-9.09279709551513,
        pmpm=1062.10405713508,
        benchmark_pmpm=1168.33872696646,
        financial_gap=-99899684,
        gross_savings_loss_yoy_pct=60.0836206408083,
        target_gross_savings_loss=146796368,
    )

    assert financial.aco_id == "A1001"
    assert financial.feature_year == 2023
    assert financial.target_year == 2024

    assert financial.benchmark_expenditure == 1098668352
    assert financial.actual_expenditure == 998768668
    assert financial.gross_savings_loss == 99899684
    assert financial.earned_shared_savings == 73426268

    assert financial.pmpm == 1062.10405713508
    assert financial.benchmark_pmpm == 1168.33872696646
    assert financial.financial_gap == -99899684