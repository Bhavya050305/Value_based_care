import { MLPrediction, SHAPFeature } from '../../types';

export interface ACOMLData {
  prediction: MLPrediction;
  shapFeatures: SHAPFeature[];
}

// DEMO DATA — Replace with SHAP API response after ML backend integration.
export const mockMLDataByACO: Record<string, ACOMLData> = {
  'abc-aco': {
    prediction: {
      riskCategory: 'LOW',
      riskProbability: 12.0,
      predictedOutcome: 'GAIN',
      expectedValue: 10458000,
      confidence: 94.0
    },
    shapFeatures: [
      { name: 'Preventive Care Rate', featureValue: '66.8%', impactValue: -0.22, direction: 'negative', explanation: 'High preventive screening rates reduce risk by detecting issues early.' },
      { name: 'Chronic Burden Management', featureValue: 'Well Controlled', impactValue: -0.15, direction: 'negative', explanation: 'Strong disease management reduces outpatient emergency events.' },
      { name: 'Readmission Rate', featureValue: '11.5%', impactValue: -0.12, direction: 'negative', explanation: 'Low post-discharge recidivism keeps costs below baseline thresholds.' },
      { name: 'ER Utilization PMPY', featureValue: '185 visits', impactValue: -0.08, direction: 'negative', explanation: 'Low emergency department usage protects contract savings.' },
      { name: 'Provider Cost Variation', featureValue: 'Minimal (2.2%)', impactValue: -0.05, direction: 'negative', explanation: 'Consistent provider charging matches regional expected cost distributions.' },
      { name: 'PMPM Baseline Gap', featureValue: '-$70.00 PMPM', impactValue: -0.03, direction: 'negative', explanation: 'Actual average expenditure sits safely below the benchmark target.' }
    ]
  },
  'xyz-aco': {
    prediction: {
      riskCategory: 'MEDIUM',
      riskProbability: 46.0,
      predictedOutcome: 'GAIN',
      expectedValue: 1008000,
      confidence: 81.0
    },
    shapFeatures: [
      { name: 'Chronic Burden Management', featureValue: 'Moderately Managed', impactValue: -0.08, direction: 'negative', explanation: 'Routine coordination keeps most chronic members stable.' },
      { name: 'Preventive Care Rate', featureValue: '59.2%', impactValue: -0.06, direction: 'negative', explanation: 'Preventive care matches baseline targets.' },
      { name: 'PMPM Baseline Gap', featureValue: '-$10.00 PMPM', impactValue: -0.02, direction: 'negative', explanation: 'A narrow margin protects current savings calculations.' },
      { name: 'Provider Cost Variation', featureValue: 'Moderate (13.0%)', impactValue: 0.05, direction: 'positive', explanation: 'Some specialist referral patterns increase contract cost distribution.' },
      { name: 'Readmission Rate', featureValue: '14.0%', impactValue: 0.08, direction: 'positive', explanation: 'Moderate readmission counts push overall expenditure upward.' },
      { name: 'ER Utilization PMPY', featureValue: '265 visits', impactValue: 0.12, direction: 'positive', explanation: 'Elevated emergency room usage creates borderline performance stress.' }
    ]
  },
  'lmn-aco': {
    prediction: {
      riskCategory: 'HIGH',
      riskProbability: 82.0,
      predictedOutcome: 'LOSS',
      expectedValue: -14040000,
      confidence: 91.0
    },
    shapFeatures: [
      { name: 'ER Utilization PMPY', featureValue: '348 visits', impactValue: 0.31, direction: 'positive', explanation: 'Excess emergency department usage significantly increases contract loss risk.' },
      { name: 'Readmission Rate', featureValue: '21.2%', impactValue: 0.24, direction: 'positive', explanation: 'High 30-day post-acute return rate adds substantial cost burden.' },
      { name: 'Provider Cost Variation', featureValue: 'Extreme (43.6%)', impactValue: 0.18, direction: 'positive', explanation: 'Wide cost differences between panel clinics indicate inefficient referral patterns.' },
      { name: 'Chronic Burden Management', featureValue: 'Poorly Managed', impactValue: 0.15, direction: 'positive', explanation: 'High concentration of unmonitored complex members leads to acute events.' },
      { name: 'PMPM Baseline Gap', featureValue: '+$75.00 PMPM', impactValue: 0.12, direction: 'positive', explanation: 'Actual average expenditure resides significantly above the baseline.' },
      { name: 'Preventive Care Rate', featureValue: '40.5%', impactValue: 0.10, direction: 'positive', explanation: 'Low primary care engagement delays critical screenings, increasing acuity.' }
    ]
  },
  'pqr-aco': {
    prediction: {
      riskCategory: 'HIGH',
      riskProbability: 68.0,
      predictedOutcome: 'LOSS',
      expectedValue: -1860000,
      confidence: 85.0
    },
    shapFeatures: [
      { name: 'Provider Cost Variation', featureValue: 'Extreme (62.6%)', impactValue: 0.28, direction: 'positive', explanation: 'Extremely high Cardiology outliers drive down overall performance.' },
      { name: 'PMPM Baseline Gap', featureValue: '+$25.00 PMPM', impactValue: 0.14, direction: 'positive', explanation: 'PMPM exceeds expected benchmarks.' },
      { name: 'Chronic Burden Management', featureValue: 'Moderately Managed', impactValue: 0.08, direction: 'positive', explanation: 'Gaps in chronic condition monitoring increase overall risk.' },
      { name: 'Readmission Rate', featureValue: '16.8%', impactValue: 0.05, direction: 'positive', explanation: 'Higher-than-average acute readmission scores add unexpected cost.' },
      { name: 'ER Utilization PMPY', featureValue: '235 visits', impactValue: -0.04, direction: 'negative', explanation: 'ER utilization is slightly below peer benchmark, helping mitigate losses.' },
      { name: 'Preventive Care Rate', featureValue: '56.5%', impactValue: -0.02, direction: 'negative', explanation: 'Preventive care provides a minor positive influence.' }
    ]
  },
  'def-aco': {
    prediction: {
      riskCategory: 'LOW',
      riskProbability: 38.0,
      predictedOutcome: 'GAIN',
      expectedValue: 2070000,
      confidence: 88.0
    },
    shapFeatures: [
      { name: 'Chronic Burden Management', featureValue: 'Intensively Managed', impactValue: -0.24, direction: 'negative', explanation: 'Aggressive complex care coordination offsets member risk score.' },
      { name: 'PMPM Baseline Gap', featureValue: '-$15.00 PMPM', impactValue: -0.10, direction: 'negative', explanation: 'Actual expenditure is lower than risk-adjusted target.' },
      { name: 'Preventive Care Rate', featureValue: '62.5%', impactValue: -0.08, direction: 'negative', explanation: 'Solid screening scores reduce acute disease escalations.' },
      { name: 'Provider Cost Variation', featureValue: 'Minimal (1.8%)', impactValue: -0.04, direction: 'negative', explanation: 'High clinician alignment prevents billing leakages.' },
      { name: 'Readmission Rate', featureValue: '13.5%', impactValue: 0.02, direction: 'positive', explanation: 'Minor readmission events increase outpatient burden slightly.' },
      { name: 'ER Utilization PMPY', featureValue: '280 visits', impactValue: 0.06, direction: 'positive', explanation: 'Elevated member acuity drives persistent ER usage.' }
    ]
  },
  'ghi-aco': {
    prediction: {
      riskCategory: 'HIGH',
      riskProbability: 79.0,
      predictedOutcome: 'LOSS',
      expectedValue: -7254000,
      confidence: 87.0
    },
    shapFeatures: [
      { name: 'ER Utilization PMPY', featureValue: '310 visits', impactValue: 0.28, direction: 'positive', explanation: 'ER utilization rate is significantly higher than regional peer baseline.' },
      { name: 'Provider Cost Variation', featureValue: 'Significant (22.3%)', impactValue: 0.16, direction: 'positive', explanation: 'Clinical pricing differences between network physicians create cost leakages.' },
      { name: 'Preventive Care Rate', featureValue: '47.2%', impactValue: 0.14, direction: 'positive', explanation: 'Low preventive rates delay treatment, escalating average disease burden.' },
      { name: 'Readmission Rate', featureValue: '19.8%', impactValue: 0.12, direction: 'positive', explanation: 'Readmission patterns are elevated, raising medical expense structures.' },
      { name: 'PMPM Baseline Gap', featureValue: '+$65.00 PMPM', impactValue: 0.08, direction: 'positive', explanation: 'Average actual PMPM exceeds target values.' },
      { name: 'Chronic Burden Management', featureValue: 'Moderately Managed', impactValue: -0.03, direction: 'negative', explanation: 'Standard chronic disease monitoring provides mild stability.' }
    ]
  }
};

export const getMLData = (acoId: string): ACOMLData => {
  return mockMLDataByACO[acoId] || mockMLDataByACO['abc-aco'];
};
export const getSHAPFeatures = (acoId: string): SHAPFeature[] => {
  return getMLData(acoId).shapFeatures;
};
