// DEMO DATA — Replace with backend peer-benchmarking / clustering output.
// Peer Target Finder identifies a realistic, evidence-based performance target
// for an ACO by benchmarking it against a cohort of similar ACOs (Current -> Peer Benchmark).

export interface SimilarPeer {
  rank: number;
  acoId: string;
  acoName: string;
  savingsRate: number;
  qualityScore: number;
  pmpm: number;
  similarityScore?: number;
  attributedMembers?: number;
}

export interface PeerTargetProfile {
  acoId: string;
  acoName: string;
  year: number;
  currentSavingsRate: number;
  currentQuality: number;
  currentPMPM: number;
  targetSavingsRate: number;
  targetQuality: number;
  targetPMPM: number;
  classification: 'Top Quartile' | 'Mid Quartile' | 'Bottom Quartile';
  similarPeers: SimilarPeer[];
  recommendation: string;
  total?: number;
  limit?: number;
  offset?: number;
  hasMore?: boolean;
}

export const mockPeerTargets: Record<string, PeerTargetProfile> = {
  'lmn-aco': {
    acoId: 'lmn-aco',
    acoName: 'LMN VBC Network',
    year: 2024,
    currentSavingsRate: -8.42,
    currentQuality: 72.1,
    currentPMPM: 965,
    targetSavingsRate: 6.2,
    targetQuality: 88.4,
    targetPMPM: 902,
    classification: 'Bottom Quartile',
    similarPeers: [
      { rank: 1, acoId: 'stuv-aco', acoName: 'STUV Regional Health', savingsRate: 7.1, qualityScore: 89.6, pmpm: 895 },
      { rank: 2, acoId: 'mno-aco', acoName: 'MNO Physician Network', savingsRate: 6.4, qualityScore: 88.2, pmpm: 905 },
      { rank: 3, acoId: 'jkl-aco', acoName: 'JKL Provider Collective', savingsRate: 5.9, qualityScore: 87.5, pmpm: 910 },
      { rank: 4, acoId: 'abc-aco', acoName: 'ABC Health Partners ACO', savingsRate: 7.36, qualityScore: 94.2, pmpm: 880 }
    ],
    recommendation: 'Prioritize ER deflection and transitional care programs — the peer cohort achieving the target profile shows materially lower ER utilization and readmission rates at similar member acuity.'
  },
  'pqr-aco': {
    acoId: 'pqr-aco',
    acoName: 'PQR Physician Syndicate',
    year: 2024,
    currentSavingsRate: -2.49,
    currentQuality: 79.0,
    currentPMPM: 1005,
    targetSavingsRate: 3.4,
    targetQuality: 84.6,
    targetPMPM: 958,
    classification: 'Bottom Quartile',
    similarPeers: [
      { rank: 1, acoId: 'wxy-aco', acoName: 'WXY Coordinated Care', savingsRate: 3.8, qualityScore: 85.1, pmpm: 950 },
      { rank: 2, acoId: 'xyz-aco', acoName: 'XYZ Care Alliance', savingsRate: 0.98, qualityScore: 86.5, pmpm: 1010 },
      { rank: 3, acoId: 'ghi-aco', acoName: 'GHI Community Health ACO', savingsRate: 1.1, qualityScore: 80.9, pmpm: 985 }
    ],
    recommendation: 'Audit specialist billing variance (notably cardiology) and standardize referral guidelines — the top peer in this cohort shows a materially tighter provider cost-variation band.'
  },
  'abc-aco': {
    acoId: 'abc-aco',
    acoName: 'ABC Health Partners ACO',
    year: 2024,
    currentSavingsRate: 7.36,
    currentQuality: 94.2,
    currentPMPM: 880,
    targetSavingsRate: 8.9,
    targetQuality: 96.0,
    targetPMPM: 862,
    classification: 'Top Quartile',
    similarPeers: [
      { rank: 1, acoId: 'stuv-aco', acoName: 'STUV Regional Health', savingsRate: 7.1, qualityScore: 89.6, pmpm: 895 },
      { rank: 2, acoId: 'mno-aco', acoName: 'MNO Physician Network', savingsRate: 6.4, qualityScore: 88.2, pmpm: 905 }
    ],
    recommendation: 'Already top-quartile — sustain preventive care compliance and monitor for drift; minor upside remains in outpatient orthopedic cost consistency.'
  },
  'xyz-aco': {
    acoId: 'xyz-aco',
    acoName: 'XYZ Care Alliance',
    year: 2024,
    currentSavingsRate: 0.98,
    currentQuality: 86.5,
    currentPMPM: 1010,
    targetSavingsRate: 4.5,
    targetQuality: 90.1,
    targetPMPM: 968,
    classification: 'Mid Quartile',
    similarPeers: [
      { rank: 1, acoId: 'wxy-aco', acoName: 'WXY Coordinated Care', savingsRate: 3.8, qualityScore: 85.1, pmpm: 950 },
      { rank: 2, acoId: 'def-aco', acoName: 'DEF Family Health Network', savingsRate: 2.6, qualityScore: 87.0, pmpm: 1120 }
    ],
    recommendation: 'Expand chronic care coordination for remote members and tighten specialist referral pathways to close the gap to peer median.'
  }
};

export const getDefaultPeerTarget = (acoId: string): PeerTargetProfile =>
  mockPeerTargets[acoId] || mockPeerTargets['lmn-aco'];
