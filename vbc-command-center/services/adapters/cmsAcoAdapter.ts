import { ACORecord, RawCMSACORecord } from '../../types/aco';

export function transformCMSACORecord(raw: RawCMSACORecord): ACORecord {
  const num = (v: any, fallback = 0) => {
    const parsed = Number(v);
    return isNaN(parsed) ? fallback : parsed;
  };

  const genSaveLoss = num(raw.GenSaveLoss, 0);

  return {
    acoId: raw.ACO_ID || 'A1001',
    acoName: raw.ACO_Name || 'Health Alliance ACO',
    agreementType: raw.Agree_Type || 'BASIC',
    currentTrack: raw.Current_Track || 'Level E',
    riskModel: raw.Risk_Model || 'Two-Sided Risk',
    assignedBeneficiaries: num(raw.N_AB, 15400),
    savingsRate: num(raw.Sav_rate, 4.2),
    generatedSavingsLoss: genSaveLoss,
    earnedSavingsLoss: num(raw.EarnSaveLoss, genSaveLoss > 0 ? genSaveLoss * 0.5 : 0),
    qualityScore: num(raw.QualScore, 92.4),
    updatedBenchmark: num(raw.UpdatedBnchmk, 11400),
    historicalBenchmark: num(raw.HistBnchmk, 11200),
    assignedBeneficiaryTotalBenchmark: num(raw.ABtotBnchmk, 175560000),
    assignedBeneficiaryTotalExpenditures: num(raw.ABtotExp, 168186400),
    finalShareRate: num(raw.FinalShareRate, 50.0),
    finalLossRate: num(raw.FinalLossRate, 30.0),
    perCapitaExpenditureTotalPY: num(raw.Per_Capita_Exp_TOTAL_PY, 10921),
    benesAge0To64: num(raw.N_Ben_Age_0_64, 1848),
    benesAge65To74: num(raw.N_Ben_Age_65_74, 6930),
    benesAge75To84: num(raw.N_Ben_Age_75_84, 4620),
    benesAge85Plus: num(raw.N_Ben_Age_85plus, 2002),
    benesFemale: num(raw.N_Ben_Female, 8624),
    benesMale: num(raw.N_Ben_Male, 6776),
    benesRaceWhite: num(raw.N_Ben_Race_White, 11550),
    benesRaceBlack: num(raw.N_Ben_Race_Black, 1848),
    benesRaceAsian: num(raw.N_Ben_Race_Asian, 770),
    benesRaceHispanic: num(raw.N_Ben_Race_Hisp, 924),
    admissionsPer1000: num(raw.ADM, 242.1),
    edVisitsPer1000: num(raw.P_EDV_Vis, 612.4),
    edVisitsHospPer1000: num(raw.P_EDV_Vis_HOSP, 184.2),
    snfLengthOfStay: num(raw.SNF_LOS, 24.8),
    snfPaymentPerStay: num(raw.SNF_PayperStay, 8420),
    performanceStatus: genSaveLoss > 500000 ? 'Shared Savings' : genSaveLoss < -200000 ? 'Shared Losses' : 'Break-even',
  };
}
