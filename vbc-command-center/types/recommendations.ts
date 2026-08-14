export interface RecommendationItem {
  id: string;
  title: string;
  category: 'Cost' | 'Utilization' | 'Quality' | 'Risk' | 'Network Alignment';
  description: string;
  impactLevel: 'High' | 'Medium' | 'Low';
  estimatedSavings: string;
  targetProviderOrAco?: string;
  status: 'Pending' | 'In Review' | 'Implemented';
  actionableSteps: string[];
}
