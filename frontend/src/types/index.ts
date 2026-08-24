export type DataMode = 'demo' | 'connected';

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  source: 'demo' | 'supabase' | 'api';
  timestamp: string;
}

export interface PerformanceDriver {
  name: string;
  current: number;
  peer: number;
  impact: 'LOW' | 'MEDIUM' | 'HIGH';
}

export interface ACO {
  id: string;
  name: string;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  attributedMembers: number;
  riskAdjustedBenchmarkPMPM: number;
  actualPMPM: number;
  savingsLoss: number; // Positive for savings, negative for loss
  savingsLossPercent: number;
  qualityScore: number; // percentage, e.g. 88
  totalExpenditure: number;
  trend: number[]; // Trend values for savings/loss or expenditure
  agreementType: string; // e.g. "Shared Savings"
  track: string; // e.g. "Enhanced / MSSP Model 3"
  startYear: number;
  benchmarkMethod: string;
  riskModel: string;
  riskScoreModel: string;
  topDriver: string;
  topProviderIssue: string;
  predictedOutcome: 'LOSS' | 'GAIN';
  riskProbability: number; // percentage, e.g. 82
}

export interface Provider {
  name: string;
  specialty: string;
  attributedMembers: number;
  actualPMPM: number;
  peerPMPM: number;
  variance: number; // percentage, e.g. 62.6
  riskFlag: 'LOW' | 'MEDIUM' | 'HIGH';
}

export interface MemberRisk {
  totalAttributed: number;
  highRiskMembers: number;
  chronicMembers: number;
  disabledMembers: number;
  averageRiskScore: number;
  benchmarkWithoutAdjustment: number;
  benchmarkWithAdjustment: number;
  riskAdjustmentImpact: number; // percentage, e.g. 8.31
  conditionPrevalence: {
    condition: string;
    rate: number; // percentage
  }[];
  attributionTrend: {
    year: number;
    total: number;
    highRisk: number;
    chronic: number;
    disabled: number;
  }[];
}

export interface SHAPFeature {
  name: string;
  featureValue: number | string;
  impactValue: number;
  direction: 'positive' | 'negative';
  explanation?: string;
}

export interface MLPrediction {
  riskCategory: 'LOW' | 'MEDIUM' | 'HIGH';
  riskProbability: number; // e.g. 82
  predictedOutcome: 'LOSS' | 'GAIN';
  expectedValue: number; // expected dollar value of savings/loss
  confidence: number; // e.g. 91
}

export interface Recommendation {
  id: string;
  recommendation: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  expectedImpact: 'LOW' | 'MEDIUM' | 'HIGH';
  reason: string;
  explanation: string;
}

export interface Alert {
  id: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'NORMAL';
  date: string;
  aco: string;
  acoId: string;
  metric: string;
  explanation: string;
  recommendedAction: string;
  status: 'active' | 'reviewed';
  score?: number;
  performanceYear?: number;
  savingsLoss?: number;
  features?: Record<string, number>;
  notes?: string;
  assignedTo?: string;
}

export interface AnomalyAlertsCounts {
  total: number;
  high: number;
  medium: number;
  low: number;
  normal: number;
}

export interface AnomalyAlertsResponseData {
  performance_year: number;
  total_acos: number;
  counts: AnomalyAlertsCounts;
  alerts: Alert[];
}

export interface AIExplanation {
  title: string;
  answer: string;
  keyPoints: string[];
  supportingMetrics?: {
    label: string;
    value: string | number;
  }[];
  recommendations?: string[];
  source: 'demo' | 'supabase' | 'api';
}

export interface LLMResponse {
  answer: string;
  keyPoints: string[];
  supportingMetrics?: {
    label: string;
    value: string | number;
  }[];
  recommendations?: string[];
  source: 'demo' | 'supabase' | 'api';
}

export interface SimulationResult {
  projectedSavings: number;
  projectedLoss: number;
  projectedExpenditure: number;
  erImpact: number;
  readmissionImpact: number;
  careCoordinationImpact: number;
  providerVariationImpact: number;
  confidence?: number;
  source: 'demo' | 'supabase' | 'api';
}
