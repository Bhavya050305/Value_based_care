import { AIExplanation, LLMResponse } from '../../types';

// DEMO DATA — Replace with backend LLM API response.
export interface MockLLMResponses {
  riskExplanations: Record<string, AIExplanation>;
  driverExplanations: Record<string, Record<string, AIExplanation>>;
  recommendations: Record<string, AIExplanation>;
  assistantAnswers: Record<string, Record<string, LLMResponse>>;
}

export const mockLLMResponses: MockLLMResponses = {
  riskExplanations: {
    'abc-aco': {
      title: 'Risk Explanation for ABC Health Partners ACO',
      answer: 'ABC Health Partners ACO is classified as LOW RISK. The model predicts a high probability (88%) of achieving shared savings (estimated gain of +$10.4M). This favorable forecast is supported by high preventive care rates and extremely low provider variation.',
      keyPoints: [
        'Preventive screening rate is 66.8%, which leads to early disease detection.',
        'Provider variation is minimal, indicating high clinic alignment with care models.',
        'Readmissions are at a low 11.5%, minimizing acute post-discharge expenses.'
      ],
      supportingMetrics: [
        { label: 'Risk Level', value: 'LOW (12.0%)' },
        { label: 'Predicted Gain', value: '+$10.4M' },
        { label: 'Quality Score', value: '94.2%' }
      ],
      source: 'demo'
    },
    'xyz-aco': {
      title: 'Risk Explanation for XYZ Care Alliance',
      answer: 'XYZ Care Alliance is in a borderline state classified as MEDIUM RISK. While the model predicts a slight gain (+$1.0M), the probability of positive contract performance is moderate (46%). This outcome is driven by balanced performance, but with notable provider variation in specialist referrals.',
      keyPoints: [
        'PMPM margin is narrow, with actual costs just $10 under benchmark.',
        'Specialist referral patterns from cardiology and oncology are slightly elevated.',
        'Chronic disease management is holding stable but requires expansion to remote members.'
      ],
      supportingMetrics: [
        { label: 'Risk Level', value: 'MEDIUM (46.0%)' },
        { label: 'Predicted Gain', value: '+$1.0M' },
        { label: 'Quality Score', value: '86.5%' }
      ],
      source: 'demo'
    },
    'lmn-aco': {
      title: 'Risk Explanation for LMN VBC Network',
      answer: 'LMN VBC Network is classified as HIGH RISK. The model predicts a high probability (82%) of a significant contract loss (estimated deficit of -$14.0M). This negative outlook is driven by substantial excess ER utilization and elevated hospital readmissions.',
      keyPoints: [
        'ER utilization is 34.8% above peer average, pushing SHAP contribution to +0.31.',
        'Readmission rate stands at 21.2%, representing the second largest risk driver (+0.24 SHAP).',
        'Extreme provider cost variation (43.6%) indicates clinical leakage and inefficient referral pathways.'
      ],
      supportingMetrics: [
        { label: 'Risk Level', value: 'HIGH (82.0%)' },
        { label: 'Predicted Loss', value: '-$14.0M' },
        { label: 'Quality Score', value: '72.1%' }
      ],
      source: 'demo'
    },
    'pqr-aco': {
      title: 'Risk Explanation for PQR Physician Syndicate',
      answer: 'PQR Physician Syndicate is classified as HIGH RISK (68% probability of loss). The model predicts a potential contract deficit of -$1.8M. The primary driver is extreme cost variation among cardiology specialists, particularly Dr. Arthur Brown.',
      keyPoints: [
        'Provider variation is extremely high, with Dr. Brown showing a +62.6% PMPM variance ($1,480 vs $890).',
        'Actual PMPM of $1,005 exceeds the risk-adjusted benchmark by $25.',
        'Chronic care coordinator ratios are lagging, leading to unmanaged diabetic care escalations.'
      ],
      supportingMetrics: [
        { label: 'Risk Level', value: 'HIGH (68.0%)' },
        { label: 'Predicted Loss', value: '-$1.8M' },
        { label: 'Quality Score', value: '82.4%' }
      ],
      source: 'demo'
    },
    'def-aco': {
      title: 'Risk Explanation for DEF Chronic Care Partners',
      answer: 'DEF Chronic Care Partners is classified as LOW RISK. Despite having a high-risk member cohort, aggressive chronic care management and intensive coordination offset the risk, leading to a predicted gain of +$2.0M.',
      keyPoints: [
        'Risk adjustment impact is +18.40%, raising the benchmark from $910 to $1,077 PMPM.',
        'Intense chronic burden management reduces acute outcomes by -24% (SHAP).',
        'Provider alignment is high, maintaining outpatient costs near peer averages.'
      ],
      supportingMetrics: [
        { label: 'Risk Level', value: 'LOW (38.0%)' },
        { label: 'Predicted Gain', value: '+$2.0M' },
        { label: 'Risk Adjustment Impact', value: '+18.40%' }
      ],
      source: 'demo'
    },
    'ghi-aco': {
      title: 'Risk Explanation for GHI Community Health ACO',
      answer: 'GHI Community Health ACO is classified as HIGH RISK. The model predicts a 79% probability of contract loss (expected deficit of -$7.2M), driven by elevated emergency room visits and low primary care preventive engagement.',
      keyPoints: [
        'ER utilization is 310 visits per 1,000 members, contributing +0.28 to SHAP.',
        'Preventive screening rates are extremely low at 47.2% (+0.14 SHAP).',
        'Clinical after-hours access is insufficient, driving non-emergent patients to local ER rooms.'
      ],
      supportingMetrics: [
        { label: 'Risk Level', value: 'HIGH (79.0%)' },
        { label: 'Predicted Loss', value: '-$7.2M' },
        { label: 'Quality Score', value: '78.6%' }
      ],
      source: 'demo'
    }
  },
  driverExplanations: {
    'lmn-aco': {
      'ER Utilization': {
        title: 'ER Utilization Driver Analysis',
        answer: 'ER utilization is 34.8% above the regional peer average (348 vs 260 visits/1k). This excess utilization is the largest driver of the predicted deficit, adding +$3.2M in preventable costs.',
        keyPoints: [
          '38% of ER visits were classified as non-emergent primary-care-treatable.',
          'Spikes occur primarily between 5:00 PM and 10:00 PM on weekdays, indicating outpatient access issues.',
          'High correlation with members lacking a completed annual wellness visit.'
        ],
        supportingMetrics: [
          { label: 'Current Rate', value: '34%' },
          { label: 'Peer Benchmark', value: '26%' },
          { label: 'SHAP Contribution', value: '+0.31' }
        ],
        source: 'demo'
      },
      'Readmission Rate': {
        title: 'Readmission Rate Driver Analysis',
        answer: 'The 30-day post-discharge readmission rate is 21.2% compared to the peer baseline of 14.5%. This is driven by gaps in post-acute transitional care management.',
        keyPoints: [
          'Only 42% of discharged patients received a nurse follow-up phone call within 48 hours.',
          'Congestive Heart Failure (CHF) and COPD members represent 60% of all readmissions.',
          'PCP appointment bookings post-discharge average 11 days, well above the 7-day recommended standard.'
        ],
        supportingMetrics: [
          { label: 'Readmission Rate', value: '21.2%' },
          { label: 'Peer Benchmark', value: '14.5%' },
          { label: 'SHAP Contribution', value: '+0.24' }
        ],
        source: 'demo'
      }
    },
    'pqr-aco': {
      'Provider Variation': {
        title: 'Provider Variation Driver Analysis',
        answer: 'Provider-level PMPM cost variation is extremely high. Cardiology procedures are the leading source of financial variance, driven by a few clinician outliers.',
        keyPoints: [
          'Dr. Arthur Brown shows a +62.6% PMPM variance ($1,480 vs $890 peer average) for cardiology members.',
          'Out-of-network specialist referrals represent 35% of all outpatient costs.',
          'Standardizing procedure guidelines across panel clinics would save up to $1.2M annually.'
        ],
        supportingMetrics: [
          { label: 'Dr. Brown PMPM', value: '$1,480' },
          { label: 'Peer Average PMPM', value: '$890' },
          { label: 'Highest Variance', value: '+62.6%' }
        ],
        source: 'demo'
      }
    }
  },
  recommendations: {
    'abc-aco': {
      title: 'AI Recommendations Summary',
      answer: 'Maintain current prevention outreach models while focusing on minor orthopedic outpatient alignment.',
      keyPoints: [
        'Wellness campaigns for members aged 75+ to avoid minor age-related utilization spikes.',
        'Negotiate standard orthopedic bundles to minimize outpatient variation.'
      ],
      source: 'demo'
    },
    'lmn-aco': {
      title: 'AI Recommendations Summary',
      answer: 'Prioritize ER deflection, transitional care management, and network leakage stabilization.',
      keyPoints: [
        'Deploy a high-risk ER deflection program, introducing after-hours advice lines and scheduling priority for acute cases.',
        'Enforce 48-hour post-discharge nurse checks and schedule PCP follow-ups within 7 days.',
        'Audit clinic referrals to restrict high-cost out-of-network leakage.'
      ],
      source: 'demo'
    },
    'pqr-aco': {
      title: 'AI Recommendations Summary',
      answer: 'Standardize cardiologist procedurals and scale chronic management.',
      keyPoints: [
        'Audit Cardiology procedures and standard billing codes to bring outlier PMPM values down to regional baselines.',
        'Assign dedicated care coordinators to hypertensive and diabetic members.'
      ],
      source: 'demo'
    }
  },
  assistantAnswers: {
    'abc-aco': {
      'why_at_risk': {
        answer: 'ABC Health Partners ACO is not currently at risk. It is predicted to achieve a surplus of +$10.4M due to low ER rates and outstanding quality performance (94.2%).',
        keyPoints: ['Preventive care is 66.8%.', 'ER visits are minimal.', 'Clinicians show high alignment.'],
        source: 'demo'
      },
      'main_drivers': {
        answer: 'The primary drivers of success for ABC ACO are high preventive screening rates and excellent care transitions.',
        keyPoints: ['Screenings are at 66.8%.', 'Readmissions are at 11.5%.'],
        source: 'demo'
      },
      'highest_variation': {
        answer: 'Provider variation is very low. All primary care physicians reside within 3% of regional peer cost baselines.',
        keyPoints: ['Dr. Jenkins shows -1.82% variance.', 'Dr. Chang shows +1.20% variance.'],
        source: 'demo'
      },
      'payer_actions': {
        answer: 'The payer should share ABC ACO\'s care coordination playbook across other network panels and monitor outpatient orthopedic referrals.',
        keyPoints: ['Replicate the preventive care model.', 'Standardize orthopedic baselines.'],
        source: 'demo'
      }
    },
    'lmn-aco': {
      'why_at_risk': {
        answer: 'LMN VBC Network is at high risk (82% probability) due to elevated ER utilization and hospital readmissions, leading to a predicted deficit of -$14.0M.',
        keyPoints: [
          'ER utilization is 34.8% above peer benchmark (+0.31 SHAP).',
          'Readmission rate stands at 21.2% (+0.24 SHAP).',
          'Clinical cost leakages exist from high-cost out-of-network referrals.'
        ],
        source: 'demo'
      },
      'main_drivers': {
        answer: 'The main negative drivers are ER utilization and acute hospital readmissions. Positive drivers include a mild chronic disease program offset.',
        keyPoints: [
          'ER visits contribute +0.31 to SHAP risk.',
          'Readmissions contribute +0.24 to SHAP risk.',
          'Out-of-network referrals add +0.18 to SHAP risk.'
        ],
        source: 'demo'
      },
      'highest_variation': {
        answer: 'The clinic with the highest variation is Dr. Thomas Wright (Cardiology) at +43.62% and Dr. Angela Baker (Internal Medicine) at +25.84%.',
        keyPoints: [
          'Dr. Wright PMPM: $1,350 vs $940 peer average.',
          'Dr. Baker PMPM: $1,120 vs $890 peer average.'
        ],
        source: 'demo'
      },
      'payer_actions': {
        answer: 'The payer must immediately launch an ER Care Management program, mandate post-discharge transitional check-ins, and audit clinical referral behaviors.',
        keyPoints: [
          'Establish after-hours clinic access.',
          'Mandate post-discharge check-ins within 48 hours.',
          'Audit outlier referral networks.'
        ],
        source: 'demo'
      }
    },
    'pqr-aco': {
      'why_at_risk': {
        answer: 'PQR Physician Syndicate is at high risk (68% probability) due to extreme provider-level cost variation in cardiology services.',
        keyPoints: [
          'Cardiology cost variation adds +0.28 to SHAP.',
          'Actual PMPM is $1,005 compared to the benchmark of $980.'
        ],
        source: 'demo'
      },
      'main_drivers': {
        answer: 'The primary driver is provider variation. Secondary drivers include gaps in care management and chronic condition monitoring.',
        keyPoints: [
          'Cardiology variance (Dr. Brown) adds +0.28 to SHAP.',
          'Average member chronic burden is unmonitored.'
        ],
        source: 'demo'
      },
      'highest_variation': {
        answer: 'Dr. Arthur Brown (Cardiology) has the highest variation at +62.60% ($1,480 PMPM vs $890 peer average).',
        keyPoints: [
          'Dr. Brown: +62.6% variance.',
          'Dr. Patricia Hall: +22.22% variance.'
        ],
        source: 'demo'
      },
      'payer_actions': {
        answer: 'The payer should review Dr. Brown\'s procedural claims, standardize care pathways for cardiac members, and deploy care coordinators.',
        keyPoints: [
          'Review cardiology claims codes.',
          'Deploy care coordinators for diabetic members.'
        ],
        source: 'demo'
      }
    }
  }
};

export const getRiskExplanationLLM = (acoId: string): AIExplanation => {
  return mockLLMResponses.riskExplanations[acoId] || mockLLMResponses.riskExplanations['abc-aco'];
};

export const getDriverExplanationLLM = (acoId: string, driverName: string): AIExplanation => {
  const acoDrivers = mockLLMResponses.driverExplanations[acoId];
  if (acoDrivers && acoDrivers[driverName]) {
    return acoDrivers[driverName];
  }
  
  // Generic fallback if not matched
  return {
    title: `${driverName} Explanation`,
    answer: `${driverName} is showing some variance. The current value differs from the peer benchmark by a small margin, leading to minor SHAP impact. Reviewing patient files and optimizing care scheduling is recommended.`,
    keyPoints: [
      'Encourage regular preventive checkups.',
      'Check coding compliance in outpatient files.'
    ],
    supportingMetrics: [
      { label: 'Driver', value: driverName }
    ],
    source: 'demo'
  };
};

export const getRecommendationsLLM = (acoId: string): AIExplanation => {
  return mockLLMResponses.recommendations[acoId] || mockLLMResponses.recommendations['abc-aco'];
};

export const getAssistantAnswerLLM = (questionKey: string, acoId: string): LLMResponse => {
  const acoAnswers = mockLLMResponses.assistantAnswers[acoId];
  if (acoAnswers && acoAnswers[questionKey]) {
    return acoAnswers[questionKey];
  }
  
  // Fallback to default answers
  return {
    answer: `Regarding this question for ${acoId || 'this ACO'}, the analytics dashboard reveals stable performance under the current contract year. Expanding chronic disease monitoring and auditing provider outpatient variation are the recommended courses of action.`,
    keyPoints: [
      'Continue monitoring baseline trends.',
      'Provide regular provider variance scorecards.'
    ],
    source: 'demo'
  };
};
