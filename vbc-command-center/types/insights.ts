export interface AIInsight {
  id: string;
  title: string;
  category: 'Cost Driver' | 'Utilization Anomaly' | 'Risk Alignment' | 'Quality Opportunity' | 'Contract Variance';
  summary: string;
  npi?: string;
  providerName?: string;
  acoId?: string;
  acoName?: string;
  potentialDrivers: string[];
  suggestedAction: string;
  impactEstimate: string;
  confidenceScore: number;
  isDemo: boolean;
  timestamp: string;
}
