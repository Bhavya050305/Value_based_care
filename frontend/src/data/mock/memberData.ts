import { MemberRisk } from '../../types';

// DEMO DATA — Replace with Supabase/API response during final integration.
export const mockMemberRiskByACO: Record<string, MemberRisk> = {
  'abc-aco': {
    totalAttributed: 12450,
    highRiskMembers: 1045,
    chronicMembers: 4120,
    disabledMembers: 680,
    averageRiskScore: 1.04,
    benchmarkWithoutAdjustment: 842.00,
    benchmarkWithAdjustment: 912.00,
    riskAdjustmentImpact: 8.31,
    conditionPrevalence: [
      { condition: 'Hypertension', rate: 38.5 },
      { condition: 'Diabetes', rate: 24.2 },
      { condition: 'Heart Disease', rate: 12.8 },
      { condition: 'COPD / Asthma', rate: 9.5 },
      { condition: 'Depression / Anxiety', rate: 16.4 },
      { condition: 'CKD', rate: 6.2 }
    ],
    attributionTrend: [
      { year: 2021, total: 10800, highRisk: 880, chronic: 3400, disabled: 580 },
      { year: 2022, total: 11200, highRisk: 910, chronic: 3600, disabled: 610 },
      { year: 2023, total: 11800, highRisk: 970, chronic: 3850, disabled: 640 },
      { year: 2024, total: 12200, highRisk: 1010, chronic: 4010, disabled: 660 },
      { year: 2025, total: 12450, highRisk: 1045, chronic: 4120, disabled: 680 }
    ]
  },
  'xyz-aco': {
    totalAttributed: 8400,
    highRiskMembers: 920,
    chronicMembers: 3280,
    disabledMembers: 510,
    averageRiskScore: 1.12,
    benchmarkWithoutAdjustment: 910.00,
    benchmarkWithAdjustment: 1011.92,
    riskAdjustmentImpact: 11.20,
    conditionPrevalence: [
      { condition: 'Hypertension', rate: 42.1 },
      { condition: 'Diabetes', rate: 28.5 },
      { condition: 'Heart Disease', rate: 15.4 },
      { condition: 'COPD / Asthma', rate: 11.2 },
      { condition: 'Depression / Anxiety', rate: 19.8 },
      { condition: 'CKD', rate: 8.5 }
    ],
    attributionTrend: [
      { year: 2021, total: 7800, highRisk: 820, chronic: 2950, disabled: 470 },
      { year: 2022, total: 8000, highRisk: 860, chronic: 3100, disabled: 490 },
      { year: 2023, total: 8200, highRisk: 890, chronic: 3200, disabled: 500 },
      { year: 2024, total: 8350, highRisk: 910, chronic: 3250, disabled: 505 },
      { year: 2025, total: 8400, highRisk: 920, chronic: 3280, disabled: 510 }
    ]
  },
  'lmn-aco': {
    totalAttributed: 15600,
    highRiskMembers: 2450,
    chronicMembers: 7380,
    disabledMembers: 1890,
    averageRiskScore: 1.28,
    benchmarkWithoutAdjustment: 820.00,
    benchmarkWithAdjustment: 947.92,
    riskAdjustmentImpact: 15.60,
    conditionPrevalence: [
      { condition: 'Hypertension', rate: 49.6 },
      { condition: 'Diabetes', rate: 36.8 },
      { condition: 'Heart Disease', rate: 21.3 },
      { condition: 'COPD / Asthma', rate: 18.7 },
      { condition: 'Depression / Anxiety', rate: 26.5 },
      { condition: 'CKD', rate: 14.8 }
    ],
    attributionTrend: [
      { year: 2021, total: 13500, highRisk: 1980, chronic: 6100, disabled: 1510 },
      { year: 2022, total: 14200, highRisk: 2120, chronic: 6500, disabled: 1620 },
      { year: 2023, total: 14900, highRisk: 2280, chronic: 6980, disabled: 1740 },
      { year: 2024, total: 15300, highRisk: 2380, chronic: 7200, disabled: 1820 },
      { year: 2025, total: 15600, highRisk: 2450, chronic: 7380, disabled: 1890 }
    ]
  },
  'pqr-aco': {
    totalAttributed: 6200,
    highRiskMembers: 680,
    chronicMembers: 2110,
    disabledMembers: 410,
    averageRiskScore: 1.06,
    benchmarkWithoutAdjustment: 925.00,
    benchmarkWithAdjustment: 980.50,
    riskAdjustmentImpact: 6.00,
    conditionPrevalence: [
      { condition: 'Hypertension', rate: 39.8 },
      { condition: 'Diabetes', rate: 23.4 },
      { condition: 'Heart Disease', rate: 13.6 },
      { condition: 'COPD / Asthma', rate: 8.9 },
      { condition: 'Depression / Anxiety', rate: 15.2 },
      { condition: 'CKD', rate: 7.1 }
    ],
    attributionTrend: [
      { year: 2021, total: 5800, highRisk: 610, chronic: 1950, disabled: 370 },
      { year: 2022, total: 6000, highRisk: 650, chronic: 2020, disabled: 390 },
      { year: 2023, total: 6150, highRisk: 670, chronic: 2080, disabled: 405 },
      { year: 2024, total: 6200, highRisk: 680, chronic: 2110, disabled: 410 },
      { year: 2025, total: 6200, highRisk: 680, chronic: 2110, disabled: 410 }
    ]
  },
  'def-aco': {
    totalAttributed: 11500,
    highRiskMembers: 2185, // Scenario E: High Member Risk Burden
    chronicMembers: 6210,
    disabledMembers: 1725,
    averageRiskScore: 1.34,
    benchmarkWithoutAdjustment: 910.00,
    benchmarkWithAdjustment: 1077.44, // +18.4% impact
    riskAdjustmentImpact: 18.40,
    conditionPrevalence: [
      { condition: 'Hypertension', rate: 54.2 },
      { condition: 'Diabetes', rate: 41.5 },
      { condition: 'Heart Disease', rate: 26.8 },
      { condition: 'COPD / Asthma', rate: 22.4 },
      { condition: 'Depression / Anxiety', rate: 29.1 },
      { condition: 'CKD', rate: 18.9 }
    ],
    attributionTrend: [
      { year: 2021, total: 9500, highRisk: 1650, chronic: 4900, disabled: 1310 },
      { year: 2022, total: 10200, highRisk: 1840, chronic: 5350, disabled: 1450 },
      { year: 2023, total: 10800, highRisk: 2010, chronic: 5780, disabled: 1590 },
      { year: 2024, total: 11200, highRisk: 2110, chronic: 6020, disabled: 1675 },
      { year: 2025, total: 11500, highRisk: 2185, chronic: 6210, disabled: 1725 }
    ]
  },
  'ghi-aco': {
    totalAttributed: 9300,
    highRiskMembers: 1120,
    chronicMembers: 3620,
    disabledMembers: 740,
    averageRiskScore: 1.07,
    benchmarkWithoutAdjustment: 850.47,
    benchmarkWithAdjustment: 910.00,
    riskAdjustmentImpact: 7.00,
    conditionPrevalence: [
      { condition: 'Hypertension', rate: 41.2 },
      { condition: 'Diabetes', rate: 25.8 },
      { condition: 'Heart Disease', rate: 14.1 },
      { condition: 'COPD / Asthma', rate: 10.8 },
      { condition: 'Depression / Anxiety', rate: 18.2 },
      { condition: 'CKD', rate: 7.9 }
    ],
    attributionTrend: [
      { year: 2021, total: 8500, highRisk: 980, chronic: 3100, disabled: 650 },
      { year: 2022, total: 8800, highRisk: 1020, chronic: 3300, disabled: 680 },
      { year: 2023, total: 9100, highRisk: 1080, chronic: 3500, disabled: 710 },
      { year: 2024, total: 9250, highRisk: 1110, chronic: 3580, disabled: 730 },
      { year: 2025, total: 9300, highRisk: 1120, chronic: 3620, disabled: 740 }
    ]
  }
};

// Fallback logic for remaining ACOs
export const getMemberRiskData = (acoId: string): MemberRisk => {
  return mockMemberRiskByACO[acoId] || mockMemberRiskByACO['abc-aco'];
};
