// DEMO DATA — Replace with backend forecast model output during final integration.
// Forecast is NOT risk classification and NOT peer prediction. It is purely
// Historical (actual, solid line) -> Predicted (forecast, dashed line).

export type ForecastQuality = 'High' | 'Medium' | 'Low';
export type ForecastTrend = 'Positive' | 'Negative' | 'Stable';

export interface ForecastYearPoint {
  year: number;
  savingsRatePercent: number | null; // null for years without an actual value (kept sparse on purpose)
  pmpm: number | null;
  expenditure: number | null;
  qualityScore: number | null;
  isPredicted: boolean;
}

export interface ACOForecast {
  acoId: string;
  series: ForecastYearPoint[];
  lastActualYear: number;
  predictedYear: number;
  lastActualSavingsRate: number;
  predictedSavingsRate: number;
  expectedChangePp: number; // percentage points
  trend: ForecastTrend;
  forecastQuality: ForecastQuality;
}

export const mockACOForecasts: Record<string, ACOForecast> = {
  'abc-aco': {
    acoId: 'abc-aco',
    series: [
      { year: 2020, savingsRatePercent: 4.2, pmpm: 940, expenditure: 118400000, qualityScore: 90.1, isPredicted: false },
      { year: 2021, savingsRatePercent: 5.8, pmpm: 920, expenditure: 124200000, qualityScore: 91.4, isPredicted: false },
      { year: 2022, savingsRatePercent: 6.4, pmpm: 905, expenditure: 130800000, qualityScore: 92.5, isPredicted: false },
      { year: 2023, savingsRatePercent: 6.9, pmpm: 892, expenditure: 136500000, qualityScore: 93.3, isPredicted: false },
      { year: 2024, savingsRatePercent: 7.36, pmpm: 880, expenditure: 131560000, qualityScore: 94.2, isPredicted: false },
      { year: 2025, savingsRatePercent: 8.1, pmpm: 868, expenditure: 138900000, qualityScore: 94.9, isPredicted: true }
    ],
    lastActualYear: 2024,
    predictedYear: 2025,
    lastActualSavingsRate: 7.36,
    predictedSavingsRate: 8.1,
    expectedChangePp: 0.74,
    trend: 'Positive',
    forecastQuality: 'High'
  },
  'xyz-aco': {
    acoId: 'xyz-aco',
    series: [
      { year: 2020, savingsRatePercent: 1.1, pmpm: 1040, expenditure: 92100000, qualityScore: 82.0, isPredicted: false },
      { year: 2021, savingsRatePercent: 1.4, pmpm: 1032, expenditure: 95200000, qualityScore: 83.6, isPredicted: false },
      { year: 2022, savingsRatePercent: 0.9, pmpm: 1024, expenditure: 98100000, qualityScore: 84.8, isPredicted: false },
      { year: 2023, savingsRatePercent: 0.85, pmpm: 1016, expenditure: 99800000, qualityScore: 85.6, isPredicted: false },
      { year: 2024, savingsRatePercent: 0.98, pmpm: 1010, expenditure: 101808000, qualityScore: 86.5, isPredicted: false },
      { year: 2025, savingsRatePercent: 1.35, pmpm: 1002, expenditure: 103500000, qualityScore: 87.2, isPredicted: true }
    ],
    lastActualYear: 2024,
    predictedYear: 2025,
    lastActualSavingsRate: 0.98,
    predictedSavingsRate: 1.35,
    expectedChangePp: 0.37,
    trend: 'Positive',
    forecastQuality: 'Medium'
  },
  'lmn-aco': {
    acoId: 'lmn-aco',
    series: [
      { year: 2020, savingsRatePercent: -4.4, pmpm: 890, expenditure: 139100000, qualityScore: 78.2, isPredicted: false },
      { year: 2021, savingsRatePercent: -5.6, pmpm: 915, expenditure: 145600000, qualityScore: 76.5, isPredicted: false },
      { year: 2022, savingsRatePercent: -7.1, pmpm: 935, expenditure: 152100000, qualityScore: 74.8, isPredicted: false },
      { year: 2023, savingsRatePercent: -8.0, pmpm: 950, expenditure: 158900000, qualityScore: 73.2, isPredicted: false },
      { year: 2024, savingsRatePercent: -10.72, pmpm: 965, expenditure: 180648000, qualityScore: 72.1, isPredicted: false },
      { year: 2025, savingsRatePercent: 0.31, pmpm: 918, expenditure: 168200000, qualityScore: 75.4, isPredicted: true }
    ],
    lastActualYear: 2024,
    predictedYear: 2025,
    lastActualSavingsRate: -10.72,
    predictedSavingsRate: 0.31,
    expectedChangePp: 11.03,
    trend: 'Positive',
    forecastQuality: 'High'
  },
  'pqr-aco': {
    acoId: 'pqr-aco',
    series: [
      { year: 2020, savingsRatePercent: -0.4, pmpm: 985, expenditure: 68100000, qualityScore: 81.5, isPredicted: false },
      { year: 2021, savingsRatePercent: -1.0, pmpm: 992, expenditure: 69400000, qualityScore: 80.9, isPredicted: false },
      { year: 2022, savingsRatePercent: -1.3, pmpm: 998, expenditure: 70900000, qualityScore: 80.1, isPredicted: false },
      { year: 2023, savingsRatePercent: -1.5, pmpm: 1001, expenditure: 72100000, qualityScore: 79.6, isPredicted: false },
      { year: 2024, savingsRatePercent: -2.49, pmpm: 1005, expenditure: 74772000, qualityScore: 79.0, isPredicted: false },
      { year: 2025, savingsRatePercent: -1.6, pmpm: 995, expenditure: 73600000, qualityScore: 79.8, isPredicted: true }
    ],
    lastActualYear: 2024,
    predictedYear: 2025,
    lastActualSavingsRate: -2.49,
    predictedSavingsRate: -1.6,
    expectedChangePp: 0.89,
    trend: 'Positive',
    forecastQuality: 'Medium'
  }
};

// Portfolio-level (aggregate) forecast, separate from individual ACO forecasts.
export const mockPortfolioForecast: ACOForecast = {
  acoId: 'portfolio',
  series: [
    { year: 2020, savingsRatePercent: 1.9, pmpm: null, expenditure: 2800000000, qualityScore: 85.0, isPredicted: false },
    { year: 2021, savingsRatePercent: 2.2, pmpm: null, expenditure: 2850000000, qualityScore: 86.1, isPredicted: false },
    { year: 2022, savingsRatePercent: 2.4, pmpm: null, expenditure: 2920000000, qualityScore: 86.9, isPredicted: false },
    { year: 2023, savingsRatePercent: 2.5, pmpm: null, expenditure: 3010000000, qualityScore: 87.4, isPredicted: false },
    { year: 2024, savingsRatePercent: 2.64, pmpm: null, expenditure: 3120000000, qualityScore: 88.0, isPredicted: false },
    { year: 2025, savingsRatePercent: 3.05, pmpm: null, expenditure: 3195000000, qualityScore: 88.6, isPredicted: true }
  ],
  lastActualYear: 2024,
  predictedYear: 2025,
  lastActualSavingsRate: 2.64,
  predictedSavingsRate: 3.05,
  expectedChangePp: 0.41,
  trend: 'Positive',
  forecastQuality: 'High'
};
