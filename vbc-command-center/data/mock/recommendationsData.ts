import { RecommendationItem } from '../../types/recommendations';

export const mockRecommendations: RecommendationItem[] = [
  {
    id: 'REC-3001',
    title: 'Review high-utilization cardiology & nephrology providers',
    category: 'Utilization',
    description: 'Investigate top 5% of providers exceeding 8.0 services per beneficiary threshold to identify unbundled HCPCS codes or duplicate lab testing.',
    impactLevel: 'High',
    estimatedSavings: '$2.4M',
    targetProviderOrAco: 'Metropolitan Cardiology & Pacific Renal Care',
    status: 'Pending',
    actionableSteps: [
      'Extract line-item HCPCS claims for providers with services/bene > 8.0',
      'Compare procedure frequencies against CMS regional peer percentiles',
      'Schedule clinical peer review with provider medical directors',
    ],
  },
  {
    id: 'REC-3002',
    title: 'Investigate providers with high payment variance',
    category: 'Cost',
    description: 'Audit specialty practices where submitted charges exceed Medicare allowed amounts by over 150% to optimize contract fee schedules.',
    impactLevel: 'High',
    estimatedSavings: '$1.8M',
    targetProviderOrAco: 'Dr. Robert Chen & Dr. Elena Rostova',
    status: 'In Review',
    actionableSteps: [
      'Identify procedures with high charge-to-allowed ratios',
      'Benchmark facility vs non-facility place of service pricing',
      'Renegotiate out-of-network wrap contracts for high-volume specialists',
    ],
  },
  {
    id: 'REC-3003',
    title: 'Enhance chronic condition management for high-risk cohorts',
    category: 'Quality',
    description: 'Implement multi-disciplinary disease management programs for beneficiaries with hypertension, diabetes, and heart failure overlap.',
    impactLevel: 'Medium',
    estimatedSavings: '$1.1M',
    targetProviderOrAco: 'Health Alliance ACO & Florida Senior Care',
    status: 'Implemented',
    actionableSteps: [
      'Identify multi-morbid patients (3+ chronic conditions)',
      'Assign dedicated nurse care managers for home tele-monitoring',
      'Schedule quarterly medication reconciliation reviews',
    ],
  },
  {
    id: 'REC-3004',
    title: 'Compare provider performance with regional peers',
    category: 'Network Alignment',
    description: 'Publish quarterly provider scorecard dashboard detailing risk-adjusted cost efficiency, quality score, and patient retention metrics.',
    impactLevel: 'Medium',
    estimatedSavings: '$750K',
    targetProviderOrAco: 'All Participating ACO Providers',
    status: 'Pending',
    actionableSteps: [
      'Generate peer comparison reports for all contracted NPIs',
      'Deliver transparent performance transparency summaries to practice leaders',
      'Establish value-based incentive bonus distribution criteria',
    ],
  },
];
