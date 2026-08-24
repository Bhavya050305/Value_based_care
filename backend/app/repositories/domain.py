"""Domain repository classes for database data access."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import (
    ACO,
    ACOFinancialMLTraining,
    ActionRecord,
    AuditLogRecord,
    OutcomeRecord,
    PerformanceQuality,
    PredictionRecord,
    RecommendationRecord,
    ReportRecord,
    SimulationRecord,
    UserProfile,
    UserPreferenceRecord,
)

from app.repositories.base import BaseRepository


# ============================================================
# ACO
# ============================================================

class ACORepository(BaseRepository[ACO]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ACO, session)

    async def get_by_aco_id(
        self,
        aco_id: str,
        organization_id: str | None = None,
    ) -> ACO | None:

        query = select(ACO).where(
            ACO.aco_id == aco_id
        )

        if organization_id:
            query = query.where(
                (ACO.organization_id == organization_id)
                | (ACO.organization_id.is_(None))
            )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()


# ============================================================
# FINANCIAL
# ============================================================

class PerformanceRepository(
    BaseRepository[ACOFinancialMLTraining]
):
    """
    Repository for precomputed financial data.

    No financial calculations are performed here.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            ACOFinancialMLTraining,
            session,
        )

    async def get_financial_by_year(
        self,
        aco_id: str,
        target_year: int,
    ) -> ACOFinancialMLTraining | None:

        query = (
            select(ACOFinancialMLTraining)
            .where(
                ACOFinancialMLTraining.ACO_ID == aco_id,
                ACOFinancialMLTraining.target_year == target_year,
            )
            .limit(1)
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def get_financial_summary(
        self,
        aco_id: str,
    ) -> Sequence[ACOFinancialMLTraining]:

        query = (
            select(ACOFinancialMLTraining)
            .where(
                ACOFinancialMLTraining.ACO_ID == aco_id
            )
            .order_by(
                ACOFinancialMLTraining.target_year.desc()
            )
        )

        result = await self.session.execute(query)

        return result.scalars().all()

    async def get_financial_years(
        self,
        aco_id: str,
    ) -> Sequence[int]:

        query = (
            select(
                ACOFinancialMLTraining.target_year
            )
            .where(
                ACOFinancialMLTraining.ACO_ID == aco_id
            )
            .distinct()
            .order_by(
                ACOFinancialMLTraining.target_year.desc()
            )
        )

        result = await self.session.execute(query)

        return result.scalars().all()


# ============================================================
# QUALITY
# ============================================================

class PerformanceQualityRepository(
    BaseRepository[PerformanceQuality]
):

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            PerformanceQuality,
            session,
        )

    async def get_by_year(
        self,
        aco_id: str,
        performance_year: int,
    ) -> PerformanceQuality | None:

        query = (
            select(PerformanceQuality)
            .where(
                PerformanceQuality.aco_id == aco_id,
                PerformanceQuality.performance_year == performance_year,
            )
            .limit(1)
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def get_history(
        self,
        aco_id: str,
    ) -> Sequence[PerformanceQuality]:

        query = (
            select(PerformanceQuality)
            .where(
                PerformanceQuality.aco_id == aco_id
            )
            .order_by(
                PerformanceQuality.performance_year.desc()
            )
        )

        result = await self.session.execute(query)

        return result.scalars().all()


# ============================================================
# PREDICTIONS
# ============================================================

class PredictionRepository(
    BaseRepository[PredictionRecord]
):

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            PredictionRecord,
            session,
        )

    async def get_latest_prediction(
        self,
        aco_id: str,
        organization_id: str | None = None,
    ) -> PredictionRecord | None:

        query = select(PredictionRecord).where(
            PredictionRecord.aco_id == aco_id
        )

        if organization_id:
            query = query.where(
                (PredictionRecord.organization_id == organization_id)
                | (PredictionRecord.organization_id.is_(None))
            )

        query = query.order_by(
            PredictionRecord.created_at.desc()
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()


# ============================================================
# RECOMMENDATIONS
# ============================================================

class RecommendationRepository(
    BaseRepository[RecommendationRecord]
):

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            RecommendationRecord,
            session,
        )


# ============================================================
# ACTIONS
# ============================================================

class ActionRepository(
    BaseRepository[ActionRecord]
):

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            ActionRecord,
            session,
        )


# ============================================================
# AUDIT
# ============================================================

class AuditRepository(
    BaseRepository[AuditLogRecord]
):

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            AuditLogRecord,
            session,
        )


# ============================================================
# SIMULATIONS
# ============================================================

class SimulationRepository(
    BaseRepository[SimulationRecord]
):

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            SimulationRecord,
            session,
        )

    async def list_by_aco_id(
        self,
        aco_id: str,
        organization_id: str | None = None,
    ) -> Sequence[SimulationRecord]:

        query = select(SimulationRecord).where(
            SimulationRecord.aco_id == aco_id
        )

        if organization_id:
            query = query.where(
                (SimulationRecord.organization_id == organization_id)
                | (SimulationRecord.organization_id.is_(None))
            )

        query = query.order_by(
            SimulationRecord.created_at.desc()
        )

        result = await self.session.execute(query)

        return result.scalars().all()


# ============================================================
# OUTCOMES
# ============================================================

class OutcomeRepository(
    BaseRepository[OutcomeRecord]
):

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            OutcomeRecord,
            session,
        )

    async def list_by_action_id(
        self,
        action_id: str,
        organization_id: str | None = None,
    ) -> Sequence[OutcomeRecord]:

        query = select(OutcomeRecord).where(
            OutcomeRecord.action_id == action_id
        )

        if organization_id:
            query = query.where(
                (OutcomeRecord.organization_id == organization_id)
                | (OutcomeRecord.organization_id.is_(None))
            )

        result = await self.session.execute(query)

        return result.scalars().all()


# ============================================================
# REPORTS
# ============================================================

class ReportRepository(
    BaseRepository[ReportRecord]
):

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            ReportRecord,
            session,
        )


# ============================================================
# USER PROFILE
# ============================================================

class UserProfileRepository(
    BaseRepository[UserProfile]
):

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            UserProfile,
            session,
        )

    async def get_by_user_id(
        self,
        user_id: str,
    ) -> UserProfile | None:

        query = select(UserProfile).where(
            UserProfile.id == user_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()


# ============================================================
# USER PREFERENCES
# ============================================================

class UserPreferenceRepository(
    BaseRepository[UserPreferenceRecord]
):

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            UserPreferenceRecord,
            session,
        )

    async def get_by_user_id(
        self,
        user_id: str,
    ) -> UserPreferenceRecord | None:

        query = select(UserPreferenceRecord).where(
            UserPreferenceRecord.user_id == user_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()