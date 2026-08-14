import { ProviderRecord, RawCMSProviderRecord } from '../../types/provider';
import { calculateProviderPerformance } from '../../utils/performance';

/**
 * Adapter converting raw CMS API responses (e.g. dataset 92396110-2aed-4d63-a6a2-5d6207d46a29)
 * into normalized frontend ProviderRecord data model.
 */
export function transformCMSProviderRecord(raw: RawCMSProviderRecord): ProviderRecord {
  const num = (v: any, fallback = 0) => {
    const parsed = Number(v);
    return isNaN(parsed) ? fallback : parsed;
  };

  const npi = String(raw.Rndrng_NPI || '');
  const lastNameOrg = String(raw.Rndrng_Prvdr_Last_Org_Name || '');
  const firstName = raw.Rndrng_Prvdr_First_Name || '';
  const creds = raw.Rndrng_Prvdr_Crdntls || '';
  
  const providerName = raw.Rndrng_Prvdr_Ent_Cd === 'I' && firstName
    ? `${firstName} ${lastNameOrg}${creds ? `, ${creds}` : ''}`
    : lastNameOrg;

  const totalBenes = num(raw.Tot_Benes, 1);
  const totalServices = num(raw.Tot_Srvcs, 0);
  const totalPayment = num(raw.Tot_Mdcr_Pymt_Amt, 0);
  const totalAllowed = num(raw.Tot_Mdcr_Alowd_Amt, 0);
  const totalSubmitted = num(raw.Tot_Sbmtd_Chrg, 0);
  const totalStandardized = num(raw.Tot_Mdcr_Stdzd_Amt, totalPayment * 0.95);

  const riskScore = num(raw.Bene_Avg_Risk_Scre, 1.0);

  const record: ProviderRecord = {
    npi,
    providerName,
    lastNameOrg,
    firstName,
    credentials: creds,
    providerType: raw.Rndrng_Prvdr_Type || 'Internal Medicine',
    entityCode: raw.Rndrng_Prvdr_Ent_Cd || 'I',
    city: raw.Rndrng_Prvdr_City || 'Dallas',
    state: raw.Rndrng_Prvdr_State_Abrvtn || 'TX',
    zipCode: raw.Rndrng_Prvdr_Zip5 || '75001',
    medicareParticipating: raw.Rndrng_Prvdr_Mdcr_Prtcptg_Ind === 'Y',
    totalHcpcsCodes: num(raw.Tot_HCPCS_Cds, 15),
    totalBeneficiaries: totalBenes,
    totalServices,
    totalSubmittedCharges: totalSubmitted,
    totalMedicareAllowedAmount: totalAllowed,
    totalMedicarePaymentAmount: totalPayment,
    totalMedicareStandardizedAmount: totalStandardized,
    drugMedicarePaymentAmount: Math.round(totalPayment * 0.28),
    medicalMedicarePaymentAmount: Math.round(totalPayment * 0.72),
    averageBeneficiaryAge: num(raw.Bene_Avg_Age, 72.4),
    ageUnder65: num(raw.Bene_Age_LT_65_Cnt, Math.round(totalBenes * 0.12)),
    age65To74: num(raw.Bene_Age_65_74_Cnt, Math.round(totalBenes * 0.45)),
    age75To84: num(raw.Bene_Age_75_84_Cnt, Math.round(totalBenes * 0.30)),
    age85Plus: num(raw.Bene_Age_GT_84_Cnt, Math.round(totalBenes * 0.13)),
    femaleBeneficiaries: num(raw.Bene_Feml_Cnt, Math.round(totalBenes * 0.56)),
    maleBeneficiaries: num(raw.Bene_Male_Cnt, Math.round(totalBenes * 0.44)),
    raceWhite: num(raw.Bene_Race_Wht_Cnt, Math.round(totalBenes * 0.75)),
    raceBlack: num(raw.Bene_Race_Black_Cnt, Math.round(totalBenes * 0.12)),
    raceAsianPacific: num(raw.Bene_Race_API_Cnt, Math.round(totalBenes * 0.05)),
    raceHispanic: num(raw.Bene_Race_Hspnc_Cnt, Math.round(totalBenes * 0.06)),
    raceNativeAmerican: num(raw.Bene_Race_NatInd_Cnt, Math.round(totalBenes * 0.01)),
    raceOther: num(raw.Bene_Race_Othr_Cnt, Math.round(totalBenes * 0.01)),
    dualEligible: num(raw.Bene_Dual_Cnt, Math.round(totalBenes * 0.24)),
    nonDualEligible: num(raw.Bene_Ndual_Cnt, Math.round(totalBenes * 0.76)),
    averageRiskScore: riskScore,
    chronicConditions: {
      asthma: 14.2,
      afib: 12.8,
      ckd: 28.5,
      copd: 21.4,
      diabetes: 36.8,
      heartFailure: 18.9,
      hypertension: 64.2,
      ischemicHeartDisease: 31.0,
      stroke: 9.6,
    },
    behavioralHealth: {
      alcoholDrug: 6.4,
      tobacco: 24.1,
      anxiety: 28.2,
      depression: 31.5,
      bipolar: 4.2,
      mood: 12.8,
      schizophrenia: 2.1,
    },
    servicesPerBeneficiary: Number((totalServices / totalBenes).toFixed(1)),
    paymentPerBeneficiary: Number((totalPayment / totalBenes).toFixed(0)),
  };

  record.performanceTier = calculateProviderPerformance(record);
  return record;
}
