export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  suggestedActions?: string[];
  dataRef?: {
    npi?: string;
    acoId?: string;
  };
}

export function queryAssistant(userQuery: string): ChatMessage {
  const query = userQuery.toLowerCase();
  
  if (query.includes('metropolitan cardiology') || query.includes('1982736450') || query.includes('performing poorly') || query.includes('why is provider')) {
    return {
      id: `msg-${Date.now()}`,
      sender: 'assistant',
      text: `**Analysis for Metropolitan Cardiology Associates PA (NPI: 1982736450)**:

• **Medicare Payments**: $10.15M total ($2,643 / beneficiary), which is **42% above peer benchmarks**.
• **Utilization Drivers**: High density of advanced diagnostic imaging (SPECT, echocardiography) with 7.5 services / beneficiary.
• **Risk Profile**: High average beneficiary risk score (1.64 HCC) with elevated chronic heart failure (42.1%) and afib (38.6%) prevalence.

**Recommended Payer Action**: Initiate prior authorization review for repeat outpatient echocardiograms and engage medical director for peer-to-peer billing review.`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      suggestedActions: ['View Provider Detail Page', 'View Utilization Analysis', 'Generate Audit Letter'],
      dataRef: { npi: '1982736450' },
    };
  }

  if (query.includes('utilization') || query.includes('high volume') || query.includes('unusually high')) {
    return {
      id: `msg-${Date.now()}`,
      sender: 'assistant',
      text: `**High Utilization Anomaly Report**:

1. **Pacific Renal Care Center (NPI: 1847362510)**: 9.8 services / beneficiary (Benchmark: 5.2). Driven by frequent outpatient dialysis lab panels.
2. **Dr. Marcus Vance (NPI: 1357924680)**: 8.8 services / beneficiary (Benchmark: 4.8). Driven by high COPD patient complexity and ED visit frequency.
3. **Dr. Elena Rostova (NPI: 1298374650)**: 9.3 services / beneficiary due to intensive oncology infusion therapies.`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      suggestedActions: ['Open Cost & Utilization Page', 'Filter by High Utilization'],
    };
  }

  if (query.includes('cost drivers') || query.includes('main cost') || query.includes('payments')) {
    return {
      id: `msg-${Date.now()}`,
      sender: 'assistant',
      text: `**Contract Primary Cost Drivers (PY 2024)**:

• **Total Medicare Spending**: **$43.26M Allowed / $34.46M Paid** across 15,690 beneficiaries.
• **Top Specialty Spend**: Cardiology ($10.15M), Nephrology ($7.85M), Oncology ($7.12M).
• **Drug vs Medical Split**: Drug spending accounts for **28.4%** ($9.8M), while Medical spending accounts for **71.6%** ($24.6M).`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      suggestedActions: ['View Command Center Overview', 'Export Cost Summary CSV'],
    };
  }

  if (query.includes('risk') || query.includes('high risk score')) {
    return {
      id: `msg-${Date.now()}`,
      sender: 'assistant',
      text: `**Beneficiary Risk Profile Summary**:

• **Contract Average Risk Score**: **1.34** (National baseline: 1.00).
• **Highest Risk Provider**: Pacific Renal Care Center (1.82 Risk Score).
• **Chronic Condition Drivers**: Hypertension (68.4%), Diabetes (38.2%), CKD (29.8%), COPD (22.0%).`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      suggestedActions: ['View Beneficiary Profile', 'Run Risk Alignment Simulation'],
    };
  }

  // Default response
  return {
    id: `msg-${Date.now()}`,
    sender: 'assistant',
    text: `Based on current value-based contract performance metrics:

• Total Medicare Contract Spending: **$34.46M Payment Amount**
• Active ACO Contracts: **5 ACOs** (3 Shared Savings, 1 Shared Losses, 1 Break-even)
• Total Contracted Providers: **8 Key Provider Entities / 15,690 Beneficiaries**

What specific provider, ACO, or cost metric would you like me to analyze further?`,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    suggestedActions: ['Show High Risk Providers', 'Show ACO Savings Summary', 'Analyze Utilization'],
  };
}
