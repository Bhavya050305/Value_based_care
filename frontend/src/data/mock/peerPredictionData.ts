// DEMO DATA — Replace with backend peer-prediction model output.
// Peer Prediction is DISTINCT from Forecast: forecast projects an ACO's own
// historical-future trajectory; peer prediction estimates how an ACO is
// expected to perform relative to a modeled peer cohort in the current year.

export interface PeerPrediction {
  acoId: string;
  predictedPeerSavingsRate: number;
  predictedPeerQuality: number;
  predictedPeerPMPM: number;
  percentileRank: number; // 0-100, where the ACO is predicted to land among peers
  classification: 'Outperforming' | 'On Par' | 'Underperforming';
}

export const mockPeerPredictions: Record<string, PeerPrediction> = {
  'abc-aco': { acoId: 'abc-aco', predictedPeerSavingsRate: 6.4, predictedPeerQuality: 90.2, predictedPeerPMPM: 905, percentileRank: 88, classification: 'Outperforming' },
  'xyz-aco': { acoId: 'xyz-aco', predictedPeerSavingsRate: 1.6, predictedPeerQuality: 84.9, predictedPeerPMPM: 995, percentileRank: 52, classification: 'On Par' },
  'lmn-aco': { acoId: 'lmn-aco', predictedPeerSavingsRate: -2.1, predictedPeerQuality: 79.5, predictedPeerPMPM: 915, percentileRank: 9, classification: 'Underperforming' },
  'pqr-aco': { acoId: 'pqr-aco', predictedPeerSavingsRate: 0.4, predictedPeerQuality: 81.0, predictedPeerPMPM: 970, percentileRank: 31, classification: 'Underperforming' },
  'def-aco': { acoId: 'def-aco', predictedPeerSavingsRate: 3.1, predictedPeerQuality: 85.5, predictedPeerPMPM: 1120, percentileRank: 61, classification: 'On Par' },
  'ghi-aco': { acoId: 'ghi-aco', predictedPeerSavingsRate: 1.2, predictedPeerQuality: 80.5, predictedPeerPMPM: 960, percentileRank: 38, classification: 'Underperforming' }
};
