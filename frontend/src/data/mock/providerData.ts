import { Provider } from '../../types';

// DEMO DATA — Replace with Supabase/API response during final integration.
export const mockProvidersByACO: Record<string, Provider[]> = {
  'abc-aco': [
    { name: 'Dr. Sarah Jenkins', specialty: 'Family Medicine', attributedMembers: 820, actualPMPM: 810, peerPMPM: 825, variance: -1.82, riskFlag: 'LOW' },
    { name: 'Dr. Michael Chang', specialty: 'Internal Medicine', attributedMembers: 950, actualPMPM: 840, peerPMPM: 830, variance: 1.20, riskFlag: 'LOW' },
    { name: 'Dr. Lisa Ross', specialty: 'Geriatrics', attributedMembers: 420, actualPMPM: 990, peerPMPM: 970, variance: 2.06, riskFlag: 'LOW' },
    { name: 'Dr. David Smith', specialty: 'Family Medicine', attributedMembers: 760, actualPMPM: 805, peerPMPM: 825, variance: -2.42, riskFlag: 'LOW' },
    { name: 'Dr. Karen Todd', specialty: 'Cardiology', attributedMembers: 310, actualPMPM: 910, peerPMPM: 890, variance: 2.25, riskFlag: 'LOW' }
  ],
  'xyz-aco': [
    { name: 'Dr. Robert Carter', specialty: 'Family Medicine', attributedMembers: 680, actualPMPM: 910, peerPMPM: 850, variance: 7.06, riskFlag: 'MEDIUM' },
    { name: 'Dr. Elena Rostova', specialty: 'Internal Medicine', attributedMembers: 720, actualPMPM: 890, peerPMPM: 860, variance: 3.49, riskFlag: 'LOW' },
    { name: 'Dr. James Lee', specialty: 'Cardiology', attributedMembers: 240, actualPMPM: 1040, peerPMPM: 920, variance: 13.04, riskFlag: 'MEDIUM' },
    { name: 'Dr. Susan Miller', specialty: 'Family Medicine', attributedMembers: 810, actualPMPM: 845, peerPMPM: 850, variance: -0.59, riskFlag: 'LOW' }
  ],
  'lmn-aco': [
    { name: 'Dr. Angela Baker', specialty: 'Internal Medicine', attributedMembers: 1100, actualPMPM: 1120, peerPMPM: 890, variance: 25.84, riskFlag: 'HIGH' },
    { name: 'Dr. Thomas Wright', specialty: 'Cardiology', attributedMembers: 380, actualPMPM: 1350, peerPMPM: 940, variance: 43.62, riskFlag: 'HIGH' },
    { name: 'Dr. Chloe Benoit', specialty: 'Family Medicine', attributedMembers: 950, actualPMPM: 980, peerPMPM: 820, variance: 19.51, riskFlag: 'MEDIUM' },
    { name: 'Dr. Joshua King', specialty: 'Pulmonology', attributedMembers: 410, actualPMPM: 1200, peerPMPM: 960, variance: 25.00, riskFlag: 'HIGH' }
  ],
  'pqr-aco': [
    { name: 'Dr. Arthur Brown', specialty: 'Cardiology', attributedMembers: 480, actualPMPM: 1480, peerPMPM: 890, variance: 62.60, riskFlag: 'HIGH' }, // +62.6% cardiologist
    { name: 'Dr. Helen Davis', specialty: 'Internal Medicine', attributedMembers: 640, actualPMPM: 860, peerPMPM: 880, variance: -2.27, riskFlag: 'LOW' },
    { name: 'Dr. George Vance', specialty: 'Family Medicine', attributedMembers: 980, actualPMPM: 810, peerPMPM: 825, variance: -1.82, riskFlag: 'LOW' },
    { name: 'Dr. Patricia Hall', specialty: 'Geriatrics', attributedMembers: 390, actualPMPM: 1210, peerPMPM: 990, variance: 22.22, riskFlag: 'HIGH' }
  ],
  'def-aco': [
    { name: 'Dr. Sandra Diaz', specialty: 'Internal Medicine', attributedMembers: 840, actualPMPM: 1130, peerPMPM: 1110, variance: 1.80, riskFlag: 'LOW' },
    { name: 'Dr. Richard Fox', specialty: 'Geriatrics', attributedMembers: 620, actualPMPM: 1150, peerPMPM: 1180, variance: -2.54, riskFlag: 'LOW' },
    { name: 'Dr. Keith Nelson', specialty: 'Endocrinology', attributedMembers: 550, actualPMPM: 1220, peerPMPM: 1210, variance: 0.83, riskFlag: 'LOW' }
  ],
  'ghi-aco': [
    { name: 'Dr. Timothy Webb', specialty: 'Family Medicine', attributedMembers: 920, actualPMPM: 1040, peerPMPM: 850, variance: 22.35, riskFlag: 'HIGH' },
    { name: 'Dr. Marie DuPont', specialty: 'Internal Medicine', attributedMembers: 840, actualPMPM: 980, peerPMPM: 860, variance: 13.95, riskFlag: 'MEDIUM' },
    { name: 'Dr. Steven Wu', specialty: 'Cardiology', attributedMembers: 210, actualPMPM: 1150, peerPMPM: 920, variance: 25.00, riskFlag: 'HIGH' }
  ],
  'jkl-aco': [
    { name: 'Dr. Rebecca Young', specialty: 'Family Medicine', attributedMembers: 1200, actualPMPM: 830, peerPMPM: 850, variance: -2.35, riskFlag: 'LOW' },
    { name: 'Dr. Walter White', specialty: 'Internal Medicine', attributedMembers: 1150, actualPMPM: 840, peerPMPM: 860, variance: -2.33, riskFlag: 'LOW' }
  ],
  'mno-aco': [
    { name: 'Dr. Gary Peters', specialty: 'Family Medicine', attributedMembers: 850, actualPMPM: 890, peerPMPM: 840, variance: 5.95, riskFlag: 'MEDIUM' },
    { name: 'Dr. Nancy Clark', specialty: 'Internal Medicine', attributedMembers: 920, actualPMPM: 875, peerPMPM: 850, variance: 2.94, riskFlag: 'LOW' }
  ],
  'stuv-aco': [
    { name: 'Dr. Samuel Jackson', specialty: 'Internal Medicine', attributedMembers: 780, actualPMPM: 1030, peerPMPM: 1010, variance: 1.98, riskFlag: 'LOW' },
    { name: 'Dr. Diana Prince', specialty: 'Cardiology', attributedMembers: 310, actualPMPM: 1120, peerPMPM: 1080, variance: 3.70, riskFlag: 'LOW' }
  ],
  'wxy-aco': [
    { name: 'Dr. Brian Oconner', specialty: 'Internal Medicine', attributedMembers: 1250, actualPMPM: 1180, peerPMPM: 950, variance: 24.21, riskFlag: 'HIGH' },
    { name: 'Dr. Letty Ortiz', specialty: 'Cardiology', attributedMembers: 410, actualPMPM: 1390, peerPMPM: 980, variance: 41.84, riskFlag: 'HIGH' },
    { name: 'Dr. Roman Pearce', specialty: 'Family Medicine', attributedMembers: 1100, actualPMPM: 990, peerPMPM: 890, variance: 11.24, riskFlag: 'MEDIUM' }
  ]
};

// Fallback provider list for generic lookups
export const defaultProviders: Provider[] = [
  { name: 'Dr. Arthur Brown', specialty: 'Cardiology', attributedMembers: 480, actualPMPM: 1480, peerPMPM: 890, variance: 62.60, riskFlag: 'HIGH' },
  { name: 'Dr. Sarah Jenkins', specialty: 'Family Medicine', attributedMembers: 820, actualPMPM: 810, peerPMPM: 825, variance: -1.82, riskFlag: 'LOW' },
  { name: 'Dr. Michael Chang', specialty: 'Internal Medicine', attributedMembers: 950, actualPMPM: 840, peerPMPM: 830, variance: 1.20, riskFlag: 'LOW' },
  { name: 'Dr. Thomas Wright', specialty: 'Cardiology', attributedMembers: 380, actualPMPM: 1350, peerPMPM: 940, variance: 43.62, riskFlag: 'HIGH' }
];
