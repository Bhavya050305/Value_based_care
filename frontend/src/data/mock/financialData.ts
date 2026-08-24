export interface PortfolioSummary {
  totalACOs: number;
  goodStanding: number;
  needsAttention: number;
  atRisk: number;
  totalSavings: number;
  totalLoss: number;
  totalExpenditure: number;
  riskAdjustedBenchmark: number;
  riskAdjustmentImpact: number;
}

export interface FinancialTrendPoint {
  year: number;
  savings: number;
  loss: number;
  actualExpenditure: number;
  benchmarkExpenditure: number;
}

export interface ACOFinancialTrendPoint {
  year: number;
  actualExpenditure: number;
  benchmarkExpenditure: number;
  savingsLoss: number;
}

// DEMO DATA — Replace with calculated backend response.
export const mockPortfolioSummary: PortfolioSummary = {
  totalACOs: 57,
  goodStanding: 31,
  needsAttention: 17,
  atRisk: 9,
  totalSavings: 82400000,
  totalLoss: -23800000,
  totalExpenditure: 3120000000,
  riskAdjustedBenchmark: 3040000000,
  riskAdjustmentImpact: 9.35
};

export const mockPortfolioFinancialTrend: FinancialTrendPoint[] = [
  { year: 2021, savings: 61500000, loss: -18200000, actualExpenditure: 2850000000, benchmarkExpenditure: 2800000000 },
  { year: 2022, savings: 68900000, loss: -19500000, actualExpenditure: 2920000000, benchmarkExpenditure: 2880000000 },
  { year: 2023, savings: 74200000, loss: -21800000, actualExpenditure: 3010000000, benchmarkExpenditure: 2950000000 },
  { year: 2024, savings: 79500000, loss: -22400000, actualExpenditure: 3060000000, benchmarkExpenditure: 3000000000 },
  { year: 2025, savings: 82400000, loss: -23800000, actualExpenditure: 3120000000, benchmarkExpenditure: 3040000000 }
];

export const mockACOFinancialTrend: Record<string, ACOFinancialTrendPoint[]> = {
  'abc-aco': [
    { year: 2021, actualExpenditure: 110500000, benchmarkExpenditure: 118400000, savingsLoss: 7900000 },
    { year: 2022, actualExpenditure: 115200000, benchmarkExpenditure: 124200000, savingsLoss: 9000000 },
    { year: 2023, actualExpenditure: 121000000, benchmarkExpenditure: 130800000, savingsLoss: 9800000 },
    { year: 2024, actualExpenditure: 126400000, benchmarkExpenditure: 136500000, savingsLoss: 10100000 },
    { year: 2025, actualExpenditure: 131560000, benchmarkExpenditure: 142018000, savingsLoss: 10458000 }
  ],
  'xyz-aco': [
    { year: 2021, actualExpenditure: 95400000, benchmarkExpenditure: 95200000, savingsLoss: -200000 },
    { year: 2022, actualExpenditure: 97800000, benchmarkExpenditure: 98100000, savingsLoss: 300000 },
    { year: 2023, actualExpenditure: 99100000, benchmarkExpenditure: 99800000, savingsLoss: 700000 },
    { year: 2024, actualExpenditure: 100500000, benchmarkExpenditure: 101400000, savingsLoss: 900000 },
    { year: 2025, actualExpenditure: 101808000, benchmarkExpenditure: 102816000, savingsLoss: 1008000 }
  ],
  'lmn-aco': [
    { year: 2021, actualExpenditure: 145200000, benchmarkExpenditure: 139100000, savingsLoss: -6100000 },
    { year: 2022, actualExpenditure: 153800000, benchmarkExpenditure: 145600000, savingsLoss: -8200000 },
    { year: 2023, actualExpenditure: 162900000, benchmarkExpenditure: 152100000, savingsLoss: -10800000 },
    { year: 2024, actualExpenditure: 171400000, benchmarkExpenditure: 158900000, savingsLoss: -12500000 },
    { year: 2025, actualExpenditure: 180648000, benchmarkExpenditure: 166608000, savingsLoss: -14040000 }
  ],
  'pqr-aco': [
    { year: 2021, actualExpenditure: 68400000, benchmarkExpenditure: 68100000, savingsLoss: -300000 },
    { year: 2022, actualExpenditure: 70100000, benchmarkExpenditure: 69400000, savingsLoss: -700000 },
    { year: 2023, actualExpenditure: 71800000, benchmarkExpenditure: 70900000, savingsLoss: -900000 },
    { year: 2024, actualExpenditure: 73200000, benchmarkExpenditure: 72100000, savingsLoss: -1100000 },
    { year: 2025, actualExpenditure: 74772000, benchmarkExpenditure: 72912000, savingsLoss: -1860000 }
  ]
};

export const getACOFinancialTrend = (acoId: string): ACOFinancialTrendPoint[] => {
  return mockACOFinancialTrend[acoId] || mockACOFinancialTrend['abc-aco'];
};
