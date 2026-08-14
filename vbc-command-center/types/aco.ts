// Normalized TypeScript model for CMS ACO Datasets

export interface ACORecord {
  acoId: string; // ACO_ID
  acoName: string; // ACO_Name
  agreementType: string; // Agree_Type
  currentTrack: string; // Current_Track
  riskModel: string; // Risk_Model
  assignedBeneficiaries: number; // N_AB

  savingsRate: number; // Sav_rate
  generatedSavingsLoss: number; // GenSaveLoss
  earnedSavingsLoss: number; // EarnSaveLoss
  qualityScore: number; // QualScore

  updatedBenchmark: number; // UpdatedBnchmk
  historicalBenchmark: number; // HistBnchmk
  assignedBeneficiaryTotalBenchmark: number; // ABtotBnchmk
  assignedBeneficiaryTotalExpenditures: number; // ABtotExp

  finalShareRate: number; // FinalShareRate
  finalLossRate: number; // FinalLossRate
  perCapitaExpenditureTotalPY: number; // Per_Capita_Exp_TOTAL_PY

  // Age Breakdown
  benesAge0To64: number; // N_Ben_Age_0_64
  benesAge65To74: number; // N_Ben_Age_65_74
  benesAge75To84: number; // N_Ben_Age_75_84
  benesAge85Plus: number; // N_Ben_Age_85plus

  // Gender & Demographics
  benesFemale: number; // N_Ben_Female
  benesMale: number; // N_Ben_Male
  benesRaceWhite: number; // N_Ben_Race_White
  benesRaceBlack: number; // N_Ben_Race_Black
  benesRaceAsian: number; // N_Ben_Race_Asian
  benesRaceHispanic: number; // N_Ben_Race_Hisp

  // Utilization & Quality Markers
  admissionsPer1000: number; // ADM
  edVisitsPer1000: number; // P_EDV_Vis
  edVisitsHospPer1000: number; // P_EDV_Vis_HOSP
  snfLengthOfStay: number; // SNF_LOS
  snfPaymentPerStay: number; // SNF_PayperStay

  performanceStatus: 'Shared Savings' | 'Shared Losses' | 'Break-even';
}

export interface RawCMSACORecord {
  ACO_ID: string;
  ACO_Name: string;
  Agree_Type: string;
  Current_Track: string;
  Risk_Model: string;
  N_AB: number | string;
  Sav_rate: number | string;
  GenSaveLoss: number | string;
  EarnSaveLoss: number | string;
  QualScore: number | string;
  UpdatedBnchmk: number | string;
  HistBnchmk: number | string;
  ABtotBnchmk: number | string;
  ABtotExp: number | string;
  FinalShareRate: number | string;
  FinalLossRate: number | string;
  Per_Capita_Exp_TOTAL_PY: number | string;
  N_Ben_Age_0_64?: number | string;
  N_Ben_Age_65_74?: number | string;
  N_Ben_Age_75_84?: number | string;
  N_Ben_Age_85plus?: number | string;
  N_Ben_Female?: number | string;
  N_Ben_Male?: number | string;
  N_Ben_Race_White?: number | string;
  N_Ben_Race_Black?: number | string;
  N_Ben_Race_Asian?: number | string;
  N_Ben_Race_Hisp?: number | string;
  ADM?: number | string;
  P_EDV_Vis?: number | string;
  P_EDV_Vis_HOSP?: number | string;
  SNF_LOS?: number | string;
  SNF_PayperStay?: number | string;
}
