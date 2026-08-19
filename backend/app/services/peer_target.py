import math
from typing import Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import HTTPException

from app.core.config import SUPPORTED_YEARS, YEAR_TABLE_MAP
from app.schemas.peer_target import (
    PeerTargetRequest,
    PeerTargetResponse,
    PeerItem,
    TargetAcoSummary,
    OpportunityGap,
)
from app.ml.peer_target.predictor import get_peer_target_predictor


class PeerTargetService:

    async def get_peer_targets(
        self,
        aco_id: str,
        performance_year: int = 2024,
        limit: int = 20,
        offset: int = 0,
        db: Optional[AsyncSession] = None,
        features: Optional[Dict[str, float]] = None,
    ) -> PeerTargetResponse:
        year = performance_year if performance_year in YEAR_TABLE_MAP else 2024
        table = YEAR_TABLE_MAP[year]

        if db is not None:
            # 1. Fetch Target ACO
            target_sql = f"""
                SELECT 
                    "ACO_ID", "ACO_Name", "ACO_State", "Agree_Type", "Risk_Model",
                    "N_AB", "ABtotBnchmk", "ABtotExp", "GenSaveLoss", "EarnSaveLoss",
                    "SavingsLossPct", "PMPM", "BenchmarkPMPM", "QualScore"
                FROM public.{table}
                WHERE "ACO_ID" = :aco_id LIMIT 1;
            """
            t_res = await db.execute(text(target_sql), {"aco_id": aco_id})
            t_row = t_res.fetchone()

            if not t_row:
                # If target ACO not found, attempt first available ACO in table
                fallback_sql = f"""
                    SELECT "ACO_ID" FROM public.{table} ORDER BY "ACO_ID" ASC LIMIT 1;
                """
                fb_res = await db.execute(text(fallback_sql))
                fb_row = fb_res.fetchone()
                if fb_row:
                    aco_id = str(fb_row[0])
                    t_res = await db.execute(text(target_sql), {"aco_id": aco_id})
                    t_row = t_res.fetchone()

            if t_row:
                target_id = str(t_row[0])
                target_name = str(t_row[1])
                target_members = int(t_row[5]) if t_row[5] is not None else 10000
                target_savings_loss = float(t_row[8]) if t_row[8] is not None else 0.0
                target_savings_pct = float(t_row[10]) if t_row[10] is not None else 0.0
                target_pmpm = float(t_row[11]) if t_row[11] is not None else 1000.0
                target_bm_pmpm = float(t_row[12]) if t_row[12] is not None else 1000.0
                target_qual = float(t_row[13]) if t_row[13] is not None else 85.0

                # 2. Fetch candidate cohort
                cohort_sql = f"""
                    SELECT 
                        "ACO_ID", "ACO_Name", "ACO_State", "Agree_Type",
                        "N_AB", "SavingsLossPct", "PMPM", "BenchmarkPMPM", "QualScore", "GenSaveLoss"
                    FROM public.{table}
                    WHERE "ACO_ID" != :aco_id;
                """
                c_res = await db.execute(text(cohort_sql), {"aco_id": target_id})
                c_rows = c_res.fetchall()

                # 3. Calculate similarity score for each candidate
                scored_peers: List[PeerItem] = []
                for row in c_rows:
                    p_id = str(row[0])
                    p_name = str(row[1])
                    p_state = str(row[2]) if row[2] else "US"
                    p_track = str(row[3]) if row[3] else "MSSP Track 1+"
                    p_members = int(row[4]) if row[4] is not None else 0
                    p_sav_pct = float(row[5]) if row[5] is not None else 0.0
                    p_pmpm = float(row[6]) if row[6] is not None else 0.0
                    p_bm_pmpm = float(row[7]) if row[7] is not None else 0.0
                    p_qual = float(row[8]) if row[8] is not None else 0.0

                    # Compute normalized feature distances
                    d_members = abs(target_members - p_members) / max(1000, target_members)
                    d_pmpm = abs(target_pmpm - p_pmpm) / max(100.0, target_pmpm)
                    d_bm_pmpm = abs(target_bm_pmpm - p_bm_pmpm) / max(100.0, target_bm_pmpm)
                    d_sav = abs(target_savings_pct - p_sav_pct) / 10.0
                    d_qual = abs(target_qual - p_qual) / 20.0

                    total_dist = math.sqrt(
                        0.3 * (d_members ** 2) +
                        0.3 * (d_pmpm ** 2) +
                        0.2 * (d_bm_pmpm ** 2) +
                        0.1 * (d_sav ** 2) +
                        0.1 * (d_qual ** 2)
                    )

                    similarity = max(50.0, min(99.9, round((1.0 / (1.0 + total_dist)) * 100.0, 1)))

                    scored_peers.append(
                        PeerItem(
                            rank=0,
                            aco_id=p_id,
                            aco_name=p_name,
                            savings_rate=p_sav_pct,
                            quality_score=p_qual,
                            pmpm=p_pmpm,
                            benchmark_pmpm=p_bm_pmpm,
                            attributed_members=p_members,
                            similarity_score=similarity,
                            state=p_state,
                            track=p_track,
                        )
                    )

                # Sort by similarity score descending
                scored_peers.sort(key=lambda x: x.similarity_score, reverse=True)

                total_peers = len(scored_peers)
                paged_peers = scored_peers[offset : offset + limit]

                # Assign ranks strictly based on overall sorted position
                for i, peer in enumerate(paged_peers):
                    peer.rank = offset + i + 1

                has_more = (offset + limit) < total_peers

                # Compute benchmark peer target targets (top 10% high-performing peers)
                top_performers = sorted(scored_peers, key=lambda x: x.savings_rate, reverse=True)[:max(5, len(scored_peers) // 10)]
                target_sav_rate = round(sum(p.savings_rate for p in top_performers) / len(top_performers), 2) if top_performers else target_savings_pct + 2.5
                target_qual_score = round(sum(p.quality_score for p in top_performers) / len(top_performers), 1) if top_performers else max(95.0, target_qual + 2.0)
                target_pmpm_val = round(sum(p.pmpm for p in top_performers) / len(top_performers), 2) if top_performers else target_pmpm * 0.95

                classification = "Top Quartile" if target_savings_pct > 3.0 else ("Bottom Quartile" if target_savings_pct < 0.0 else "Mid Quartile")

                target_summary = TargetAcoSummary(
                    aco_id=target_id,
                    aco_name=target_name,
                    performance_year=year,
                    current_savings_rate=target_savings_pct,
                    current_quality=target_qual,
                    current_pmpm=target_pmpm,
                    target_savings_rate=target_sav_rate,
                    target_quality=target_qual_score,
                    target_pmpm=target_pmpm_val,
                    classification=classification,
                )

                opp_gap = OpportunityGap(
                    savings_gap=round(target_sav_rate - target_savings_pct, 2),
                    quality_gap=round(target_qual_score - target_qual, 1),
                    pmpm_gap=round(target_pmpm - target_pmpm_val, 2),
                    potential_gross_savings_impact=round(abs(target_savings_loss) * 0.25, 2),
                )

                rec = f"Performance benchmark derived from top quartile peer cohort in PY {year}. Focus on post-acute care management and emergency department utilization to bridge the PMPM gap of ${opp_gap.pmpm_gap:,.2f}."

                return PeerTargetResponse(
                    aco_id=target_id,
                    performance_year=year,
                    target_aco=target_summary,
                    peers=paged_peers,
                    total=total_peers,
                    limit=limit,
                    offset=offset,
                    has_more=has_more,
                    opportunity_gap=opp_gap,
                    recommendation=rec,
                    peer_indices=[i for i in range(len(paged_peers))],
                    distances=[round((100.0 - p.similarity_score) / 100.0, 3) for p in paged_peers],
                )

        # Fallback if DB is unavailable
        predictor = get_peer_target_predictor()
        result = predictor.predict(features or {})
        return PeerTargetResponse(
            aco_id=aco_id,
            performance_year=year,
            peers=[],
            total=5,
            limit=limit,
            offset=offset,
            has_more=False,
            **result,
        )

    def predict(
        self,
        aco_id: str,
        performance_year: int = 2024,
        features: Optional[Dict[str, float]] = None,
    ):
        predictor = get_peer_target_predictor()
        result = predictor.predict(features or {})
        return {
            "aco_id": aco_id,
            "performance_year": performance_year,
            **result,
        }


peer_target_service = PeerTargetService()