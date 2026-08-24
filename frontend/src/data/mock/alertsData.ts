import { Alert } from '../../types';

// DEMO DATA — Replace with Supabase/API response during final integration.
export const mockAlerts: Alert[] = [
  {
    id: 'alert-1',
    severity: 'HIGH',
    date: '2026-08-14',
    aco: 'LMN VBC Network',
    acoId: 'lmn-aco',
    metric: 'ER Utilization',
    explanation: 'ER utilization is currently 34.8% above the peer benchmark, leading to an expected $3.2M excess expenditure.',
    recommendedAction: 'Implement targeted ER deflection program and partner with local urgent care centers.',
    status: 'active'
  },
  {
    id: 'alert-2',
    severity: 'HIGH',
    date: '2026-08-13',
    aco: 'LMN VBC Network',
    acoId: 'lmn-aco',
    metric: '30-Day Readmission Rate',
    explanation: 'Readmission rates rose to 21.2% this quarter, pushing post-acute costs 18% above benchmark levels.',
    recommendedAction: 'Strengthen transitional care coordination and institute 48-hour follow-up call protocols.',
    status: 'active'
  },
  {
    id: 'alert-3',
    severity: 'HIGH',
    date: '2026-08-12',
    aco: 'PQR Physician Syndicate',
    acoId: 'pqr-aco',
    metric: 'Provider Cost Variation',
    explanation: 'Dr. Arthur Brown (Cardiology) shows +62.6% PMPM cost variation relative to peers ($1,480 vs $890).',
    recommendedAction: 'Conduct audit of cardiologist billing and review referral guidelines for coronary procedures.',
    status: 'active'
  },
  {
    id: 'alert-4',
    severity: 'MEDIUM',
    date: '2026-08-11',
    aco: 'GHI Community Health ACO',
    acoId: 'ghi-aco',
    metric: 'Preventive Care Rates',
    explanation: 'Annual screening compliance dipped to 47.2%, creating diagnostic gaps and risking future quality bonuses.',
    recommendedAction: 'Deploy automated reminder campaigns and expand telehealth wellness appointments.',
    status: 'active'
  },
  {
    id: 'alert-5',
    severity: 'MEDIUM',
    date: '2026-08-10',
    aco: 'XYZ Care Alliance',
    acoId: 'xyz-aco',
    metric: 'Chronic Burden Expense',
    explanation: 'PMPM expenditure for diabetic patients increased by 14% over regional peer trends.',
    recommendedAction: 'Initiate continuous glucose monitoring outreach and step up care coordinator assignments.',
    status: 'active'
  },
  {
    id: 'alert-6',
    severity: 'LOW',
    date: '2026-08-08',
    aco: 'ABC Health Partners ACO',
    acoId: 'abc-aco',
    metric: 'Wellness Screenings',
    explanation: 'Wellness visits for members aged 75+ decreased slightly relative to younger cohorts.',
    recommendedAction: 'Incentivize local family clinics to schedule home wellness evaluations.',
    status: 'active'
  }
];
