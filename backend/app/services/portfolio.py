"""Portfolio analytics and business intelligence service querying dedicated aco_performance_* tables via YEAR_TABLE_MAP."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.config import SUPPORTED_YEARS, YEAR_TABLE_MAP
from app.schemas.portfolio import (
    PortfolioAcoItem,
    PortfolioAlert,
    PortfolioOpportunity,
    PortfolioSummaryData,
    PortfolioTrendPoint,
    RiskDistributionItem,
)


class PortfolioService:
    """Calculates executive summary KPIs, risk distribution, and portfolio trends directly from dedicated year tables."""

    async def get_summary(
        self,
        db: AsyncSession | None = None,
        year: int | None = None,
        organization_id: str | None = None
    ) -> PortfolioSummaryData:
        if year is None or year not in YEAR_TABLE_MAP:
            raise HTTPException(
                status_code=400,
                detail=f"performance_year is required and must be one of {SUPPORTED_YEARS}",
            )

        if db is not None:
            table = YEAR_TABLE_MAP[year]
            sql = f"""
                SELECT
                    COUNT(DISTINCT "ACO_ID") AS total_acos,
                    SUM("N_AB") AS total_beneficiaries,
                    SUM("ABtotBnchmk") AS total_benchmark_expenditure,
                    SUM("ABtotExp") AS total_actual_expenditure,
                    SUM("GenSaveLoss") AS net_savings_loss,
                    SUM("EarnSaveLoss") AS earned_shared_savings,
                    AVG("QualScore") AS average_quality_score,
                    SUM(CASE WHEN "GenSaveLoss" >= 0 AND "SavingsLossPct" > 1.5 THEN 1 ELSE 0 END) AS good_standing,
                    SUM(CASE WHEN "GenSaveLoss" >= 0 AND "SavingsLossPct" <= 1.5 THEN 1 ELSE 0 END) AS needs_attention,
                    SUM(CASE WHEN "GenSaveLoss" < 0 THEN 1 ELSE 0 END) AS at_risk
                FROM public.{table}
                WHERE "ACO_ID" IS NOT NULL;
            """
            res = await db.execute(text(sql))
            row = res.first()
            if row and row[0] is not None:
                total_acos, sum_ben, sum_bm, sum_exp, sum_gross, sum_earned, avg_qual, good, att, risk = row
                return PortfolioSummaryData(
                    performance_year=year,
                    total_acos=int(total_acos or 0),
                    total_beneficiaries=int(sum_ben or 0),
                    total_benchmark_expenditure=float(sum_bm or 0.0),
                    total_actual_expenditure=float(sum_exp or 0.0),
                    net_savings_loss=float(sum_gross or 0.0),
                    earned_shared_savings=float(sum_earned or 0.0),
                    average_quality_score=round(float(avg_qual or 0.0), 4),
                    good_standing=int(good or 0),
                    needs_attention=int(att or 0),
                    at_risk=int(risk or 0),
                )

        raise HTTPException(
            status_code=404,
            detail="No data found for the selected performance year.",
        )

    async def get_risk_distribution(
        self,
        db: AsyncSession | None = None,
        year: int | None = None,
        organization_id: str | None = None
    ) -> list[RiskDistributionItem]:
        if year is None or year not in YEAR_TABLE_MAP:
            raise HTTPException(
                status_code=400,
                detail=f"performance_year is required and must be one of {SUPPORTED_YEARS}",
            )

        if db is not None:
            table = YEAR_TABLE_MAP[year]
            sql = f"""
                SELECT
                    SUM(CASE WHEN "GenSaveLoss" >= 0 AND "SavingsLossPct" > 1.5 THEN 1 ELSE 0 END) AS good,
                    SUM(CASE WHEN "GenSaveLoss" >= 0 AND "SavingsLossPct" <= 1.5 THEN 1 ELSE 0 END) AS attention,
                    SUM(CASE WHEN "GenSaveLoss" < 0 THEN 1 ELSE 0 END) AS risk,
                    COUNT(*) AS count
                FROM public.{table}
                WHERE "ACO_ID" IS NOT NULL;
            """
            res = await db.execute(text(sql))
            row = res.first()
            if row and row[3] and row[3] > 0:
                good, attention, risk, count = row[0] or 0, row[1] or 0, row[2] or 0, row[3]
                return [
                    RiskDistributionItem(risk_level="Low Risk", count=int(good), percentage=round(good / count * 100, 1)),
                    RiskDistributionItem(risk_level="Moderate Risk", count=int(attention), percentage=round(attention / count * 100, 1)),
                    RiskDistributionItem(risk_level="High Risk", count=int(risk), percentage=round(risk / count * 100, 1)),
                ]

        return []

    async def get_portfolio_trends(
        self,
        db: AsyncSession | None = None,
        organization_id: str | None = None
    ) -> list[PortfolioTrendPoint]:
        if db is not None:
            sql = """
                SELECT 2022 AS year, SUM("GenSaveLoss"), SUM("EarnSaveLoss"), AVG("QualScore"), SUM("ABtotExp"), SUM("ABtotBnchmk") FROM public.aco_performance_2022
                UNION ALL
                SELECT 2023 AS year, SUM("GenSaveLoss"), SUM("EarnSaveLoss"), AVG("QualScore"), SUM("ABtotExp"), SUM("ABtotBnchmk") FROM public.aco_performance_2023
                UNION ALL
                SELECT 2024 AS year, SUM("GenSaveLoss"), SUM("EarnSaveLoss"), AVG("QualScore"), SUM("ABtotExp"), SUM("ABtotBnchmk") FROM public.aco_performance_2024
                ORDER BY year ASC;
            """
            res = await db.execute(text(sql))
            rows = res.fetchall()
            if rows:
                return [
                    PortfolioTrendPoint(
                        performance_year=int(r[0]),
                        gross_savings_loss=float(r[1] or 0.0),
                        earned_shared_savings=float(r[2] or 0.0),
                        average_quality_score=round(float(r[3] or 0.0), 4),
                        actual_expenditure=float(r[4] or 0.0),
                        benchmark_expenditure=float(r[5] or 0.0)
                    )
                    for r in rows
                ]

        return []

    async def get_portfolio_acos(
        self,
        db: AsyncSession | None = None,
        year: int | None = None,
        organization_id: str | None = None
    ) -> list[PortfolioAcoItem]:
        if year is None or year not in YEAR_TABLE_MAP:
            raise HTTPException(
                status_code=400,
                detail=f"performance_year is required and must be one of {SUPPORTED_YEARS}",
            )

        if db is not None:
            table = YEAR_TABLE_MAP[year]
            sql = f"""
                SELECT
                    "ACO_ID",
                    "ACO_Name",
                    "ACO_State",
                    "Agree_Type",
                    "Risk_Model",
                    "GenSaveLoss",
                    "QualScore"
                FROM public.{table}
                ORDER BY "ACO_ID" ASC;
            """
            res = await db.execute(text(sql))
            rows = res.fetchall()
            if rows:
                return [
                    PortfolioAcoItem(
                        id=str(r[0]),
                        aco_id=str(r[0]),
                        name=str(r[1]),
                        state=str(r[2]) if r[2] else "US",
                        track=str(r[3]) if r[3] else "BASIC E",
                        agreement_type=str(r[4]) if r[4] else "Standard",
                        savings_loss=float(r[5] or 0.0),
                        quality_score=float(r[6] or 0.0)
                    )
                    for r in rows
                ]

        return []

    async def get_opportunities(
        self,
        db: AsyncSession | None = None,
        organization_id: str | None = None
    ) -> list[PortfolioOpportunity]:
        return []

    async def get_alerts(
        self,
        db: AsyncSession | None = None,
        organization_id: str | None = None
    ) -> list[PortfolioAlert]:
        return []
