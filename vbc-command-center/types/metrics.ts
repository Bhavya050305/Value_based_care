export interface PortfolioSummary {
  totalProviders: number;
  totalBeneficiaries: number;
  totalMedicarePayments: number;
  totalMedicareAllowed: number;
  totalServices: number;
  averageBeneficiaryAge: number;
  averageRiskScore: number;
  totalStandardizedAmount: number;

  // Comparison metrics vs previous year (%)
  paymentChangePct: number;
  allowedChangePct: number;
  beneficiariesChangePct: number;
  servicesChangePct: number;
  riskScoreChangePct: number;
}

export interface HistoricalTrendPoint {
  year: string;
  allowedAmount: number;
  paymentAmount: number;
  standardizedAmount: number;
  isDemo?: boolean;
}

export interface ProviderPerformanceDistribution {
  highPerformanceCount: number;
  moderateCount: number;
  needsAttentionCount: number;
}

export interface AlertRecord {
  id: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  category: 'High Cost' | 'High Utilization' | 'High Risk' | 'Beneficiary Mix' | 'Quality Deficit';
  npi?: string;
  providerName?: string;
  acoId?: string;
  acoName?: string;
  metricName: string;
  currentValue: string;
  benchmarkValue: string;
  variance: string;
  recommendedAction: string;
  timestamp: string;
}
