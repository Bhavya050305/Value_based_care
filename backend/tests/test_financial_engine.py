"""Unit tests for financial calculations and pipeline calculations."""

from app.pipelines.financial_pipeline import (
    calculate_expenditure_variance,
    calculate_gross_savings_loss,
)


def test_calculate_gross_savings_loss():
    # Benchmark > Actual => Positive Savings
    savings = calculate_gross_savings_loss(1000.0, 900.0)
    assert savings == 100.0

    # Benchmark < Actual => Negative Loss
    loss = calculate_gross_savings_loss(800.0, 950.0)
    assert loss == -150.0

    # None handling
    assert calculate_gross_savings_loss(None, 900.0) is None
    assert calculate_gross_savings_loss(1000.0, None) is None


def test_calculate_expenditure_variance():
    # 900 - 1000 = -100.0
    variance = calculate_expenditure_variance(1000.0, 900.0)
    assert variance == -100.0

    assert calculate_expenditure_variance(None, 900.0) is None
