// Normalized TypeScript model matching CMS Provider Datasets (e.g. 92396110-2aed-4d63-a6a2-5d6207d46a29)

export interface HcpcsServiceRecord {
  hcpcsCode: string;
  hcpcsDescription: string;
  placeOfService: string;
  beneficiaries: number;
  services: number;
  averageMedicareAllowedAmount: number;
  averageMedicarePaymentAmount: number;
  averageMedicareStandardizedAmount: number;
}

export interface ProviderRecord {
  npi: string; // Rndrng_NPI
  providerName: string; // Rndrng_Prvdr_Last_Org_Name / First / MI / Credentials
  lastNameOrg: string;
  firstName?: string;
  credentials?: string;
  providerType: string; // Rndrng_Prvdr_Type
  entityCode: 'I' | 'O'; // Rndrng_Prvdr_Ent_Cd (Individual / Organization)
  city: string; // Rndrng_Prvdr_City
  state: string; // Rndrng_Prvdr_State_Abrvtn
  zipCode: string; // Rndrng_Prvdr_Zip5

  medicareParticipating: boolean; // Rndrng_Prvdr_Mdcr_Prtcptg_Ind

  totalHcpcsCodes: number; // Tot_HCPCS_Cds
  totalBeneficiaries: number; // Tot_Benes
  totalServices: number; // Tot_Srvcs

  totalSubmittedCharges: number; // Tot_Sbmtd_Chrg
  totalMedicareAllowedAmount: number; // Tot_Mdcr_Alowd_Amt
  totalMedicarePaymentAmount: number; // Tot_Mdcr_Pymt_Amt
  totalMedicareStandardizedAmount: number; // Tot_Mdcr_Stdzd_Amt
  
  drugMedicarePaymentAmount: number; // Drug_Mdcr_Pymt_Amt
  medicalMedicarePaymentAmount: number; // Med_Mdcr_Pymt_Amt

  averageBeneficiaryAge: number; // Bene_Avg_Age

  // Age Breakdown
  ageUnder65: number; // Bene_Age_LT_65_Cnt
  age65To74: number; // Bene_Age_65_74_Cnt
  age75To84: number; // Bene_Age_75_84_Cnt
  age85Plus: number; // Bene_Age_GT_84_Cnt

  // Gender
  femaleBeneficiaries: number; // Bene_Feml_Cnt
  maleBeneficiaries: number; // Bene_Male_Cnt

  // Race / Ethnicity
  raceWhite: number; // Bene_Race_Wht_Cnt
  raceBlack: number; // Bene_Race_Black_Cnt
  raceAsianPacific: number; // Bene_Race_API_Cnt
  raceHispanic: number; // Bene_Race_Hspnc_Cnt
  raceNativeAmerican: number; // Bene_Race_NatInd_Cnt
  raceOther: number; // Bene_Race_Othr_Cnt

  // Dual Eligibility
  dualEligible: number; // Bene_Dual_Cnt
  nonDualEligible: number; // Bene_Ndual_Cnt

  // Risk Score
  averageRiskScore: number; // Bene_Avg_Risk_Scre

  // Chronic Condition Prevalence (%)
  chronicConditions: {
    asthma: number; // Bene_CC_PH_Asthma_V2_Pct
    afib: number; // Bene_CC_PH_Afib_V2_Pct
    ckd: number; // Bene_CC_PH_CKD_V2_Pct
    copd: number; // Bene_CC_PH_COPD_V2_Pct
    diabetes: number; // Bene_CC_PH_Diabetes_V2_Pct
    heartFailure: number; // Bene_CC_PH_HF_NonIHD_V2_Pct
    hypertension: number; // Bene_CC_PH_Hypertension_V2_Pct
    ischemicHeartDisease: number; // Bene_CC_PH_IschemicHeart_V2_Pct
    stroke: number; // Bene_CC_PH_Stroke_TIA_V2_Pct
  };

  // Behavioral Health Prevalence (%)
  behavioralHealth: {
    alcoholDrug: number; // Bene_CC_BH_Alcohol_Drug_V1_Pct
    tobacco: number; // Bene_CC_BH_Tobacco_V1_Pct
    anxiety: number; // Bene_CC_BH_Anxiety_V1_Pct
    depression: number; // Bene_CC_BH_Depress_V1_Pct
    bipolar: number; // Bene_CC_BH_Bipolar_V1_Pct
    mood: number; // Bene_CC_BH_Mood_V2_Pct
    schizophrenia: number; // Bene_CC_BH_Schizo_OthPsy_V1_Pct
  };

  // Associated Services
  topServices?: HcpcsServiceRecord[];

  // Computed Tiering & Benchmarks
  performanceTier?: 'High Performance' | 'Moderate' | 'Needs Attention';
  servicesPerBeneficiary?: number; // Tot_Srvcs / Tot_Benes
  paymentPerBeneficiary?: number; // Tot_Mdcr_Pymt_Amt / Tot_Benes
}

export interface RawCMSProviderRecord {
  Rndrng_NPI: string;
  Rndrng_Prvdr_Last_Org_Name: string;
  Rndrng_Prvdr_First_Name?: string;
  Rndrng_Prvdr_MI?: string;
  Rndrng_Prvdr_Crdntls?: string;
  Rndrng_Prvdr_Ent_Cd: 'I' | 'O';
  Rndrng_Prvdr_City: string;
  Rndrng_Prvdr_State_Abrvtn: string;
  Rndrng_Prvdr_Zip5: string;
  Rndrng_Prvdr_Type: string;
  Rndrng_Prvdr_Mdcr_Prtcptg_Ind: 'Y' | 'N';
  Tot_HCPCS_Cds: number | string;
  Tot_Benes: number | string;
  Tot_Srvcs: number | string;
  Tot_Sbmtd_Chrg: number | string;
  Tot_Mdcr_Alowd_Amt: number | string;
  Tot_Mdcr_Pymt_Amt: number | string;
  Tot_Mdcr_Stdzd_Amt: number | string;
  Bene_Avg_Age: number | string;
  Bene_Age_LT_65_Cnt?: number | string;
  Bene_Age_65_74_Cnt?: number | string;
  Bene_Age_75_84_Cnt?: number | string;
  Bene_Age_GT_84_Cnt?: number | string;
  Bene_Feml_Cnt?: number | string;
  Bene_Male_Cnt?: number | string;
  Bene_Race_Wht_Cnt?: number | string;
  Bene_Race_Black_Cnt?: number | string;
  Bene_Race_API_Cnt?: number | string;
  Bene_Race_Hspnc_Cnt?: number | string;
  Bene_Race_NatInd_Cnt?: number | string;
  Bene_Race_Othr_Cnt?: number | string;
  Bene_Dual_Cnt?: number | string;
  Bene_Ndual_Cnt?: number | string;
  Bene_Avg_Risk_Scre: number | string;
}
