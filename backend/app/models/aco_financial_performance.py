from __future__ import annotations

from sqlalchemy import BigInteger, Double, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class AcoFinancialPerformance(Base, TimestampMixin):
    """
    Precomputed ACO financial-performance record.

    One row = one ACO + one feature/performance year.

    IMPORTANT:
    This table is read by the API.
    Financial calculations / ML processing happen BEFORE data is
    written here.
    """

    __tablename__ = "aco_financial_performance"

    __table_args__ = (
        UniqueConstraint(
            "aco_id",
            "performance_year",
            name="uq_aco_financial_performance_aco_year",
        ),
        {"extend_existing": True},
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # ============================================================
    # IDENTIFICATION
    # ============================================================

    aco_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    performance_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    source_target_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # ============================================================
    # FINANCIAL
    # ============================================================

    benchmark_expenditure: Mapped[int | None] = mapped_column(BigInteger)
    actual_expenditure: Mapped[int | None] = mapped_column(BigInteger)
    gross_savings_loss: Mapped[int | None] = mapped_column(BigInteger)

    updated_benchmark: Mapped[int | None] = mapped_column(BigInteger)
    historical_benchmark: Mapped[int | None] = mapped_column(BigInteger)

    earned_shared_savings: Mapped[int | None] = mapped_column(BigInteger)

    share_rate: Mapped[float | None] = mapped_column(Double)
    loss_rate: Mapped[float | None] = mapped_column(Double)

    savings_loss_pct: Mapped[float | None] = mapped_column(Double)
    expenditure_variance_pct: Mapped[float | None] = mapped_column(Double)

    pmpm: Mapped[float | None] = mapped_column(Double)
    benchmark_pmpm: Mapped[float | None] = mapped_column(Double)

    financial_gap: Mapped[float | None] = mapped_column(Double)
    gross_savings_loss_yoy_pct: Mapped[float | None] = mapped_column(Double)

    target_gross_savings_loss: Mapped[float | None] = mapped_column(Double)

    # ============================================================
    # BENEFICIARY COUNTS
    # ============================================================

    n_ab: Mapped[int | None] = mapped_column(BigInteger)
    n_ab_year_py: Mapped[int | None] = mapped_column(BigInteger)
    n_ab_year_esrd_py: Mapped[int | None] = mapped_column(BigInteger)
    n_ab_year_dis_py: Mapped[int | None] = mapped_column(BigInteger)
    n_ab_year_aged_dual_py: Mapped[int | None] = mapped_column(BigInteger)
    n_ab_year_aged_nondual_py: Mapped[int | None] = mapped_column(BigInteger)

    # ============================================================
    # CMS HCC RISK
    # ============================================================

    cms_hcc_riskscore_esrd_py: Mapped[float | None] = mapped_column(Double)
    cms_hcc_riskscore_dis_py: Mapped[float | None] = mapped_column(Double)
    cms_hcc_riskscore_agdu_py: Mapped[float | None] = mapped_column(Double)
    cms_hcc_riskscore_agnd_py: Mapped[float | None] = mapped_column(Double)

    # ============================================================
    # DEMOGRAPHIC RISK
    # ============================================================

    demog_riskscore_esrd_py: Mapped[float | None] = mapped_column(Double)
    demog_riskscore_dis_py: Mapped[float | None] = mapped_column(Double)
    demog_riskscore_agdu_py: Mapped[float | None] = mapped_column(Double)
    demog_riskscore_agnd_py: Mapped[float | None] = mapped_column(Double)

    # ============================================================
    # RISK WEIGHTS
    # ============================================================

    rr_weight_esrd_py: Mapped[float | None] = mapped_column(Double)
    rr_weight_dis_py: Mapped[float | None] = mapped_column(Double)
    rr_weight_agdu_py: Mapped[float | None] = mapped_column(Double)
    rr_weight_agnd_py: Mapped[float | None] = mapped_column(Double)

    # ============================================================
    # PER CAPITA EXPENDITURE
    # ============================================================

    per_capita_exp_total_py: Mapped[float | None] = mapped_column(Double)
    per_capita_exp_all_esrd_py: Mapped[float | None] = mapped_column(Double)
    per_capita_exp_all_dis_py: Mapped[float | None] = mapped_column(Double)
    per_capita_exp_all_agdu_py: Mapped[float | None] = mapped_column(Double)
    per_capita_exp_all_agnd_py: Mapped[float | None] = mapped_column(Double)

    # ============================================================
    # ADMISSIONS
    # ============================================================

    adm: Mapped[float | None] = mapped_column(Double)
    adm_s_trm: Mapped[float | None] = mapped_column(Double)
    adm_rehab: Mapped[float | None] = mapped_column(Double)

    # ============================================================
    # EMERGENCY / IMAGING
    # ============================================================

    p_edv_vis: Mapped[float | None] = mapped_column(Double)
    p_edv_vis_hosp: Mapped[float | None] = mapped_column(Double)

    p_ct_vis: Mapped[float | None] = mapped_column(Double)
    p_mri_vis: Mapped[float | None] = mapped_column(Double)

    # ============================================================
    # E&M / VISITS
    # ============================================================

    p_em_total: Mapped[float | None] = mapped_column(Double)
    p_em_pcp_vis: Mapped[float | None] = mapped_column(Double)
    p_em_sp_vis: Mapped[float | None] = mapped_column(Double)

    p_nurse_vis: Mapped[float | None] = mapped_column(Double)
    p_fqhc_rhc_vis: Mapped[float | None] = mapped_column(Double)

    # ============================================================
    # SNF
    # ============================================================

    p_snf_adm: Mapped[float | None] = mapped_column(Double)
    snf_los: Mapped[float | None] = mapped_column(Double)
    snf_payperstay: Mapped[float | None] = mapped_column(Double)

    # ============================================================
    # CHF / PROVIDER RATE
    # ============================================================

    chf_adm: Mapped[float | None] = mapped_column(Double)
    prov_rate_1000: Mapped[float | None] = mapped_column(Double)

    # ============================================================
    # FACILITIES
    # ============================================================

    n_cah: Mapped[int | None] = mapped_column(BigInteger)
    n_fqhc: Mapped[int | None] = mapped_column(BigInteger)
    n_rhc: Mapped[int | None] = mapped_column(BigInteger)
    n_eta: Mapped[int | None] = mapped_column(BigInteger)
    n_hosp: Mapped[int | None] = mapped_column(BigInteger)
    n_fac_other: Mapped[int | None] = mapped_column(BigInteger)

    # ============================================================
    # PROVIDERS
    # ============================================================

    n_pcp: Mapped[int | None] = mapped_column(BigInteger)
    n_spec: Mapped[int | None] = mapped_column(BigInteger)
    n_np: Mapped[int | None] = mapped_column(BigInteger)
    n_pa: Mapped[int | None] = mapped_column(BigInteger)
    n_cns: Mapped[int | None] = mapped_column(BigInteger)

    # ============================================================
    # QUALITY
    # ============================================================

    qual_score: Mapped[float | None] = mapped_column(Double)

    # ============================================================
    # CONTRACT / CLASSIFICATION
    # ============================================================

    agree_type: Mapped[str | None] = mapped_column(String)
    risk_model: Mapped[str | None] = mapped_column(String)
    rev_exp_cat: Mapped[str | None] = mapped_column(String)
    assign_type: Mapped[str | None] = mapped_column(String)