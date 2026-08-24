"""Domain SQLAlchemy ORM models."""

from __future__ import annotations

import uuid

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import (
    Base,
    OrganizationScopedMixin,
    TimestampMixin,
)

from app.models.aco_financial_ml_training import (
    ACOFinancialMLTraining,
)


# ============================================================
# CANONICAL ACO YEAR ANALYTICS TABLE MODEL
# ============================================================

class AcoYearAnalytics(Base):
    __tablename__ = "aco_year_analytics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    aco_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    aco_name: Mapped[str] = mapped_column(String(255), nullable=False)
    performance_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    attributed_members: Mapped[int] = mapped_column(Integer, nullable=False)
    benchmark_expenditure: Mapped[float] = mapped_column(Float, nullable=False)
    actual_expenditure: Mapped[float] = mapped_column(Float, nullable=False)
    benchmark_pmpm: Mapped[float] = mapped_column(Float, nullable=False)
    actual_pmpm: Mapped[float] = mapped_column(Float, nullable=False)
    gross_savings_loss: Mapped[float] = mapped_column(Float, nullable=False)
    earned_shared_savings: Mapped[float] = mapped_column(Float, nullable=False)
    shared_losses: Mapped[float] = mapped_column(Float, nullable=False)
    savings_rate: Mapped[float] = mapped_column(Float, nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False)


# ============================================================
# ORGANIZATION
# ============================================================

class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )


# ============================================================
# USER PROFILE
# ============================================================

class UserProfile(
    Base,
    TimestampMixin,
    OrganizationScopedMixin,
):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        default="viewer",
        nullable=False,
    )


# ============================================================
# ACO
# ============================================================

class ACO(
    Base,
    TimestampMixin,
    OrganizationScopedMixin,
):
    __tablename__ = "acos"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    aco_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    track: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    agreement_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    risk_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )


# ============================================================
# PERFORMANCE FINANCIAL
# ============================================================

class PerformanceFinancial(
    Base,
    TimestampMixin,
    OrganizationScopedMixin,
):
    __tablename__ = "performance_financial"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    aco_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("acos.aco_id"),
        nullable=False,
        index=True,
    )

    performance_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    benchmark_expenditure: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    actual_expenditure: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    gross_savings_loss: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    earned_shared_savings: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )


# ============================================================
# PERFORMANCE QUALITY
# ============================================================

class PerformanceQuality(
    Base,
    TimestampMixin,
    OrganizationScopedMixin,
):
    __tablename__ = "performance_quality"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    aco_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("acos.aco_id"),
        nullable=False,
        index=True,
    )

    performance_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    quality_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )


# ============================================================
# PREDICTIONS
# ============================================================

class PredictionRecord(
    Base,
    TimestampMixin,
    OrganizationScopedMixin,
):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    aco_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("acos.aco_id"),
        nullable=False,
        index=True,
    )

    performance_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    model_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    model_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    predicted_savings: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    risk_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    shap_values: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )


# ============================================================
# RECOMMENDATIONS
# ============================================================

class RecommendationRecord(
    Base,
    TimestampMixin,
    OrganizationScopedMixin,
):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    aco_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("acos.aco_id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="open",
        nullable=False,
    )

    impact_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )


# ============================================================
# ACTIONS
# ============================================================

class ActionRecord(
    Base,
    TimestampMixin,
    OrganizationScopedMixin,
):
    __tablename__ = "actions"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    recommendation_id: Mapped[str | None] = mapped_column(
        String(255),
        ForeignKey("recommendations.id"),
        nullable=True,
    )

    aco_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("acos.aco_id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    assigned_to: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="in_progress",
        nullable=False,
    )


# ============================================================
# AUDIT LOG
# ============================================================

class AuditLogRecord(
    Base,
    OrganizationScopedMixin,
):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    resource: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    details: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )


# ============================================================
# SIMULATIONS
# ============================================================

class SimulationRecord(
    Base,
    TimestampMixin,
    OrganizationScopedMixin,
):
    __tablename__ = "simulations"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    aco_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("acos.aco_id"),
        nullable=False,
        index=True,
    )

    model_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    expenditure_impact: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    savings_impact: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    limitations: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )


# ============================================================
# ACTION OUTCOMES
# ============================================================

class OutcomeRecord(
    Base,
    TimestampMixin,
    OrganizationScopedMixin,
):
    __tablename__ = "action_outcomes"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    action_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("actions.id"),
        nullable=False,
        index=True,
    )

    metric_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    pre_action_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    post_action_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    measured_impact: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="measured",
        nullable=False,
    )


# ============================================================
# REPORTS
# ============================================================

class ReportRecord(
    Base,
    TimestampMixin,
    OrganizationScopedMixin,
):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    report_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    download_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    aco_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    performance_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )


# ============================================================
# USER PREFERENCES
# ============================================================

class UserPreferenceRecord(
    Base,
    TimestampMixin,
):
    __tablename__ = "user_preferences"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    theme: Mapped[str] = mapped_column(
        String(50),
        default="dark",
        nullable=False,
    )

    email_notifications: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )

    default_performance_year: Mapped[int] = mapped_column(
        Integer,
        default=2024,
        nullable=False,
    )