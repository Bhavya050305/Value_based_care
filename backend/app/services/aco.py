"""ACO Explorer domain service with Supabase database integration using YEAR_TABLE_MAP."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import HTTPException

from app.core.config import SUPPORTED_YEARS, YEAR_TABLE_MAP
from app.core.exceptions import AppError, ErrorCode
from app.schemas.aco import AcoDetail, AcoListItem


class AcoService:
    """ACO lookup, filtering, and detail resolution service."""

    async def get_performance_years(self, db: AsyncSession | None = None) -> list[int]:
        """Dynamically return supported performance years."""
        return list(SUPPORTED_YEARS)

    async def list_acos(
        self,
        db: AsyncSession | None = None,
        organization_id: str | None = None,
        search: str | None = None,
        state: str | None = None,
        track: str | None = None,
        year: int | None = None,
    ) -> list[AcoListItem]:
        if year is None or year not in YEAR_TABLE_MAP:
            raise HTTPException(
                status_code=400,
                detail=f"performance_year is required and must be one of {SUPPORTED_YEARS}",
            )

        if db is not None:
            table = YEAR_TABLE_MAP[year]
            
            where_clauses = []
            params = {}

            if search:
                where_clauses.append('("ACO_Name" ILIKE :search OR "ACO_ID" ILIKE :search)')
                params["search"] = f"%{search}%"
            if state:
                where_clauses.append('"ACO_State" = :state')
                params["state"] = state
            if track:
                where_clauses.append('("Agree_Type" = :track OR "Risk_Model" = :track)')
                params["track"] = track

            sql = f"""
                SELECT 
                    "ACO_ID",
                    "ACO_Name",
                    "N_AB",
                    "BenchmarkPMPM",
                    "PMPM",
                    "GenSaveLoss",
                    "SavingsLossPct",
                    "QualScore",
                    "ACO_State",
                    "Agree_Type",
                    "Risk_Model"
                FROM public.{table}
            """

            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)

            sql += ' ORDER BY "ACO_ID" ASC;'

            res = await db.execute(text(sql), params)
            rows = res.fetchall()

            items = []
            for r in rows:
                aco_id_val = str(r[0])
                name_val = str(r[1])
                members = int(r[2]) if r[2] is not None else 0
                bm_pmpm = float(r[3]) if r[3] is not None else 0.0
                act_pmpm = float(r[4]) if r[4] is not None else 0.0
                gen_save = float(r[5]) if r[5] is not None else 0.0
                save_pct = float(r[6]) if r[6] is not None else 0.0
                qual = float(r[7]) if r[7] is not None else 0.0
                state_val = str(r[8]) if r[8] else "US"
                track_val = str(r[9]) if r[9] else "MSSP Model"
                risk_model_val = str(r[10]) if r[10] else "Standard"

                if gen_save < 0 or save_pct < -1.0:
                    risk_lvl = "HIGH"
                elif -1.0 <= save_pct <= 1.5:
                    risk_lvl = "MEDIUM"
                else:
                    risk_lvl = "LOW"

                items.append(
                    AcoListItem(
                        id=aco_id_val,
                        aco_id=aco_id_val,
                        name=name_val,
                        state=state_val,
                        track=track_val,
                        agreement_type=risk_model_val,
                        risk_level=risk_lvl,
                        attributed_members=members,
                        benchmark_pmpm=bm_pmpm,
                        pmpm=act_pmpm,
                        savings_loss=gen_save,
                        savings_loss_pct=save_pct,
                        quality_score=qual,
                    )
                )
            return items

        return []

    async def get_aco_by_id(
        self,
        aco_id: str,
        db: AsyncSession | None = None,
        organization_id: str | None = None,
        year: int | None = None,
    ) -> AcoDetail:
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
                    "N_AB",
                    "ABtotBnchmk",
                    "ABtotExp",
                    "GenSaveLoss",
                    "EarnSaveLoss",
                    "SavingsLossPct",
                    "PMPM",
                    "BenchmarkPMPM",
                    "QualScore",
                    performance_year
                FROM public.{table} 
                WHERE UPPER(TRIM("ACO_ID")) = UPPER(TRIM(:aco_id)) LIMIT 1;
            """
            res = await db.execute(text(sql), {"aco_id": str(aco_id).strip()})
            row = res.fetchone()

            if row:
                gen_save = float(row[8]) if row[8] is not None else 0.0
                save_pct = float(row[10]) if row[10] is not None else 0.0
                if gen_save < 0 or save_pct < -1.0:
                    risk_lvl = "HIGH"
                elif -1.0 <= save_pct <= 1.5:
                    risk_lvl = "MEDIUM"
                else:
                    risk_lvl = "LOW"

                return AcoDetail(
                    id=str(row[0]),
                    aco_id=str(row[0]),
                    name=str(row[1]),
                    performance_year=int(row[14]) if row[14] is not None else year,
                    state=str(row[2]) if row[2] else "US",
                    track=str(row[3]) if row[3] else "MSSP Model",
                    agreement_type=str(row[3]) if row[3] else "Standard",
                    risk_model=str(row[4]) if row[4] else "Two-Sided Risk",
                    risk_level=risk_lvl,
                    attributed_members=int(row[5]) if row[5] is not None else 0,
                    benchmark_expenditure=float(row[6]) if row[6] is not None else 0.0,
                    actual_expenditure=float(row[7]) if row[7] is not None else 0.0,
                    savings_loss=gen_save,
                    earned_shared_savings=float(row[9]) if row[9] is not None else 0.0,
                    savings_loss_pct=save_pct,
                    pmpm=float(row[11]) if row[11] is not None else 0.0,
                    benchmark_pmpm=float(row[12]) if row[12] is not None else 0.0,
                    quality_score=float(row[13]) if row[13] is not None else 0.0,
                    created_at="2024-01-01T00:00:00Z"
                )


        raise AppError(
            code=ErrorCode.NOT_FOUND,
            message=f"No data found for ACO {aco_id} in performance year {year}.",
            status_code=404,
        )
