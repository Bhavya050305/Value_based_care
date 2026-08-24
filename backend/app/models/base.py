"""Base SQLAlchemy ORM declarative class and common mixins."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarative class for all ORM models."""


class TimestampMixin:
    """Mixin for tracking creation and modification timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class OrganizationScopedMixin:
    """Mixin for tenant isolation by organization_id."""

    organization_id: Mapped[str | None] = mapped_column(
        String(255),
        index=True,
        nullable=True,
    )
