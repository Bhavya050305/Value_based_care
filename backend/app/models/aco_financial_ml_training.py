"""
SQLAlchemy ORM model for the precomputed ACO financial dataset.

IMPORTANT:
- This model maps to the EXISTING PostgreSQL table.
- No financial calculations are performed here.
- The backend only reads precomputed values.
"""

from __future__ import annotations

from sqlalchemy import BigInteger, Double, String
from sqlalchemy.orm import Mapped, mapped_column, synonym

from app.models.base import Base


class ACOFinancialMLTraining(Base):
    __tablename__ = "aco_financial_ml_training"

    # IMPORTANT:
    # The real table is public.aco_financial_ml_training.
    __table_args__ = {
        "schema": "public",
        "extend_existing": True,
    }

    # =========================================================
    # PRIMARY KEY
    # =========================================================

    ACO_ID: Mapped[str] = mapped_column(
        "ACO_ID",
        String,
        primary_key=True,
    )

    feature_year: Mapped[int] = mapped_column(
        "feature_year",
        BigInteger,
        primary_key=True,
    )

    target_year: Mapped[int] = mapped_column(
        "target_year",
        BigInteger,
        primary_key=True,
    )

    # =========================================================
    # FINANCIAL
    # =========================================================

    ABtotBnchmk: Mapped[int | None] = mapped_column(
        "ABtotBnchmk",
        BigInteger,
    )

    ABtotExp: Mapped[int | None] = mapped_column(
        "ABtotExp",
        BigInteger,
    )

    GenSaveLoss: Mapped[int | None] = mapped_column(
        "GenSaveLoss",
        BigInteger,
    )

    UpdatedBnchmk: Mapped[int | None] = mapped_column(
        "UpdatedBnchmk",
        BigInteger,
    )

    HistBnchmk: Mapped[int | None] = mapped_column(
        "HistBnchmk",
        BigInteger,
    )

    EarnSaveLoss: Mapped[int | None] = mapped_column(
        "EarnSaveLoss",
        BigInteger,
    )

    FinalShareRate: Mapped[float | None] = mapped_column(
        "FinalShareRate",
        Double,
    )

    FinalLossRate: Mapped[float | None] = mapped_column(
        "FinalLossRate",
        Double,
    )

    # =========================================================
    # BENEFICIARY COUNTS
    # =========================================================

    N_AB: Mapped[int | None] = mapped_column(
        "N_AB",
        BigInteger,
    )

    N_AB_Year_PY: Mapped[int | None] = mapped_column(
        "N_AB_Year_PY",
        BigInteger,
    )

    N_AB_Year_ESRD_PY: Mapped[int | None] = mapped_column(
        "N_AB_Year_ESRD_PY",
        BigInteger,
    )

    N_AB_Year_DIS_PY: Mapped[int | None] = mapped_column(
        "N_AB_Year_DIS_PY",
        BigInteger,
    )

    N_AB_Year_AGED_Dual_PY: Mapped[int | None] = mapped_column(
        "N_AB_Year_AGED_Dual_PY",
        BigInteger,
    )

    N_AB_Year_AGED_NonDual_PY: Mapped[int | None] = mapped_column(
        "N_AB_Year_AGED_NonDual_PY",
        BigInteger,
    )

    # =========================================================
    # CMS HCC RISK SCORES
    # =========================================================

    CMS_HCC_RiskScore_ESRD_PY: Mapped[float | None] = mapped_column(
        "CMS_HCC_RiskScore_ESRD_PY",
        Double,
    )

    CMS_HCC_RiskScore_DIS_PY: Mapped[float | None] = mapped_column(
        "CMS_HCC_RiskScore_DIS_PY",
        Double,
    )

    CMS_HCC_RiskScore_AGDU_PY: Mapped[float | None] = mapped_column(
        "CMS_HCC_RiskScore_AGDU_PY",
        Double,
    )

    CMS_HCC_RiskScore_AGND_PY: Mapped[float | None] = mapped_column(
        "CMS_HCC_RiskScore_AGND_PY",
        Double,
    )

    # =========================================================
    # DEMOGRAPHIC RISK SCORES
    # =========================================================

    Demog_RiskScore_ESRD_PY: Mapped[float | None] = mapped_column(
        "Demog_RiskScore_ESRD_PY",
        Double,
    )

    Demog_RiskScore_DIS_PY: Mapped[float | None] = mapped_column(
        "Demog_RiskScore_DIS_PY",
        Double,
    )

    Demog_RiskScore_AGDU_PY: Mapped[float | None] = mapped_column(
        "Demog_RiskScore_AGDU_PY",
        Double,
    )

    Demog_RiskScore_AGND_PY: Mapped[float | None] = mapped_column(
        "Demog_RiskScore_AGND_PY",
        Double,
    )

    # =========================================================
    # RISK WEIGHTS
    # =========================================================

    RR_weight_ESRD_PY: Mapped[float | None] = mapped_column(
        "RR_weight_ESRD_PY",
        Double,
    )

    RR_weight_DIS_PY: Mapped[float | None] = mapped_column(
        "RR_weight_DIS_PY",
        Double,
    )

    RR_weight_AGDU_PY: Mapped[float | None] = mapped_column(
        "RR_weight_AGDU_PY",
        Double,
    )

    RR_weight_AGND_PY: Mapped[float | None] = mapped_column(
        "RR_weight_AGND_PY",
        Double,
    )

    # =========================================================
    # PER CAPITA EXPENDITURE
    # =========================================================

    Per_Capita_Exp_TOTAL_PY: Mapped[float | None] = mapped_column(
        "Per_Capita_Exp_TOTAL_PY",
        Double,
    )

    Per_Capita_Exp_ALL_ESRD_PY: Mapped[float | None] = mapped_column(
        "Per_Capita_Exp_ALL_ESRD_PY",
        Double,
    )

    Per_Capita_Exp_ALL_DIS_PY: Mapped[float | None] = mapped_column(
        "Per_Capita_Exp_ALL_DIS_PY",
        Double,
    )

    Per_Capita_Exp_ALL_AGDU_PY: Mapped[float | None] = mapped_column(
        "Per_Capita_Exp_ALL_AGDU_PY",
        Double,
    )

    Per_Capita_Exp_ALL_AGND_PY: Mapped[float | None] = mapped_column(
        "Per_Capita_Exp_ALL_AGND_PY",
        Double,
    )

    # =========================================================
    # UTILIZATION
    # =========================================================

    ADM: Mapped[float | None] = mapped_column(
        "ADM",
        Double,
    )

    ADM_S_Trm: Mapped[float | None] = mapped_column(
        "ADM_S_Trm",
        Double,
    )

    ADM_Rehab: Mapped[float | None] = mapped_column(
        "ADM_Rehab",
        Double,
    )

    P_EDV_Vis: Mapped[float | None] = mapped_column(
        "P_EDV_Vis",
        Double,
    )

    P_EDV_Vis_HOSP: Mapped[float | None] = mapped_column(
        "P_EDV_Vis_HOSP",
        Double,
    )

    P_CT_VIS: Mapped[float | None] = mapped_column(
        "P_CT_VIS",
        Double,
    )

    P_MRI_VIS: Mapped[float | None] = mapped_column(
        "P_MRI_VIS",
        Double,
    )

    P_EM_Total: Mapped[float | None] = mapped_column(
        "P_EM_Total",
        Double,
    )

    P_EM_PCP_Vis: Mapped[float | None] = mapped_column(
        "P_EM_PCP_Vis",
        Double,
    )

    P_EM_SP_Vis: Mapped[float | None] = mapped_column(
        "P_EM_SP_Vis",
        Double,
    )

    P_Nurse_Vis: Mapped[float | None] = mapped_column(
        "P_Nurse_Vis",
        Double,
    )

    P_FQHC_RHC_Vis: Mapped[float | None] = mapped_column(
        "P_FQHC_RHC_Vis",
        Double,
    )

    P_SNF_ADM: Mapped[float | None] = mapped_column(
        "P_SNF_ADM",
        Double,
    )

    SNF_LOS: Mapped[float | None] = mapped_column(
        "SNF_LOS",
        Double,
    )

    SNF_PayperStay: Mapped[float | None] = mapped_column(
        "SNF_PayperStay",
        Double,
    )

    chf_adm: Mapped[float | None] = mapped_column(
        "chf_adm",
        Double,
    )

    prov_Rate_1000: Mapped[float | None] = mapped_column(
        "prov_Rate_1000",
        Double,
    )

    # =========================================================
    # FACILITIES
    # =========================================================

    N_CAH: Mapped[int | None] = mapped_column(
        "N_CAH",
        BigInteger,
    )

    N_FQHC: Mapped[int | None] = mapped_column(
        "N_FQHC",
        BigInteger,
    )

    N_RHC: Mapped[int | None] = mapped_column(
        "N_RHC",
        BigInteger,
    )

    N_ETA: Mapped[int | None] = mapped_column(
        "N_ETA",
        BigInteger,
    )

    N_Hosp: Mapped[int | None] = mapped_column(
        "N_Hosp",
        BigInteger,
    )

    N_Fac_Other: Mapped[int | None] = mapped_column(
        "N_Fac_Other",
        BigInteger,
    )

    # =========================================================
    # PROVIDERS
    # =========================================================

    N_PCP: Mapped[int | None] = mapped_column(
        "N_PCP",
        BigInteger,
    )

    N_Spec: Mapped[int | None] = mapped_column(
        "N_Spec",
        BigInteger,
    )

    N_NP: Mapped[int | None] = mapped_column(
        "N_NP",
        BigInteger,
    )

    N_PA: Mapped[int | None] = mapped_column(
        "N_PA",
        BigInteger,
    )

    N_CNS: Mapped[int | None] = mapped_column(
        "N_CNS",
        BigInteger,
    )

    QualScore: Mapped[float | None] = mapped_column(
        "QualScore",
        Double,
    )

    # =========================================================
    # CATEGORICAL
    # =========================================================

    Agree_Type: Mapped[str | None] = mapped_column(
        "Agree_Type",
        String,
    )

    Risk_Model: Mapped[str | None] = mapped_column(
        "Risk_Model",
        String,
    )

    Rev_Exp_Cat: Mapped[str | None] = mapped_column(
        "Rev_Exp_Cat",
        String,
    )

    Assign_Type: Mapped[str | None] = mapped_column(
        "Assign_Type",
        String,
    )

    # =========================================================
    # PRECOMPUTED FINANCIAL ANALYTICS
    # =========================================================

    SavingsLossPct: Mapped[float | None] = mapped_column(
        "SavingsLossPct",
        Double,
    )

    ExpenditureVariancePct: Mapped[float | None] = mapped_column(
        "ExpenditureVariancePct",
        Double,
    )

    PMPM: Mapped[float | None] = mapped_column(
        "PMPM",
        Double,
    )

    BenchmarkPMPM: Mapped[float | None] = mapped_column(
        "BenchmarkPMPM",
        Double,
    )

    FinancialGap: Mapped[float | None] = mapped_column(
        "FinancialGap",
        Double,
    )

    GenSaveLossYoYPct: Mapped[float | None] = mapped_column(
        "GenSaveLossYoYPct",
        Double,
    )

    target_GenSaveLoss: Mapped[float | None] = mapped_column(
        "target_GenSaveLoss",
        Double,
    )

    # =========================================================
    # LOWERCASE DERIVED COLUMNS
    # =========================================================

    pmpm: Mapped[float | None] = mapped_column(
        "pmpm",
        Double,
    )

    benchmark_pmpm: Mapped[float | None] = mapped_column(
        "benchmark_pmpm",
        Double,
    )

    financial_gap: Mapped[float | None] = mapped_column(
        "financial_gap",
        Double,
    )

    savings_loss_pct: Mapped[float | None] = mapped_column(
        "savings_loss_pct",
        Double,
    )

    expenditure_variance_pct: Mapped[float | None] = mapped_column(
        "expenditure_variance_pct",
        Double,
    )

    savings_loss_yoy_pct: Mapped[float | None] = mapped_column(
        "savings_loss_yoy_pct",
        Double,
    )

    # =========================================================
    # SOURCE INFORMATION
    # =========================================================

    source_feature_year: Mapped[int | None] = mapped_column(
        "source_feature_year",
        BigInteger,
    )

    source_target_year: Mapped[int | None] = mapped_column(
        "source_target_year",
        BigInteger,
    )

    # =========================================================
    # SYNONYM ALIASES FOR COMPATIBILITY
    # =========================================================
    aco_id = synonym("ACO_ID")
    benchmark_expenditure = synonym("ABtotBnchmk")
    actual_expenditure = synonym("ABtotExp")
    gross_savings_loss = synonym("GenSaveLoss")
    earned_shared_savings = synonym("EarnSaveLoss")
    final_share_rate = synonym("FinalShareRate")
    final_loss_rate = synonym("FinalLossRate")
    gross_savings_loss_yoy_pct = synonym("GenSaveLossYoYPct")
    target_gross_savings_loss = synonym("target_GenSaveLoss")


# Alias for legacy/snake_case import compatibility
AcoFinancialMlTraining = ACOFinancialMLTraining