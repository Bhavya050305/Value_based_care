"""Generic, organization-scoped async SQLAlchemy repository base class."""

from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Base async repository providing tenant isolation and standard CRUD operations."""

    def __init__(self, model: type[T], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, id_val: str, organization_id: str | None = None) -> T | None:
        """Fetch a record by primary key, applying organization filtering if model is org-scoped."""
        query = select(self.model).where(getattr(self.model, "id") == id_val)
        if organization_id and hasattr(self.model, "organization_id"):
            query = query.where(
                (getattr(self.model, "organization_id") == organization_id)
                | (getattr(self.model, "organization_id").is_(None))
            )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_all(
        self,
        organization_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[T]:
        """Fetch records with optional tenant isolation and pagination."""
        query = select(self.model)
        if organization_id and hasattr(self.model, "organization_id"):
            query = query.where(
                (getattr(self.model, "organization_id") == organization_id)
                | (getattr(self.model, "organization_id").is_(None))
            )
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def add(self, entity: T) -> T:
        """Add a new entity record to the database session."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
