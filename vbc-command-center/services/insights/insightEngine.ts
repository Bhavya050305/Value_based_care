import { AIInsight } from '../../types/insights';
import { ProviderRecord } from '../../types/provider';
import { mockInsights } from '../../data/mock/insightsData';

export async function getPortfolioInsights(): Promise<AIInsight[]> {
  return mockInsights;
}

export function generateProviderInsights(provider: ProviderRecord): AIInsight[] {
  const insights: AIInsight[] = [];
  const servicesPerBene = provider.totalServices / (provider.totalBeneficiaries || 1);
  const paymentPerBene = provider.totalMedicarePaymentAmount / (provider.totalBeneficiaries || 1);

  if (paymentPerBene > 2500) {
    insights.push({
      id: `INS-PRV-${provider.npi}-1`,
      title: `Medicare Payment 12.8% Above Peer Benchmark`,
      category: 'Cost Driver',
      summary: `${provider.providerName} Medicare payment per beneficiary ($${paymentPerBene.toFixed(0)}) is significantly elevated relative to national peer medians.`,
      npi: provider.npi,
      providerName: provider.providerName,
      potentialDrivers: [
        'Higher service utilization frequency per patient',
        `High chronic condition complexity (Average Risk Score: ${provider.averageRiskScore})`,
        'Higher proportion of high-complexity HCPCS outpatient codes',
      ],
      suggestedAction: 'Review top high-volume HCPCS service codes and compare unit costs against regional peer practices.',
      impactEstimate: '$420K Annual Optimization Potential',
      confidenceScore: 0.92,
      isDemo: true,
      timestamp: 'Just now',
    });
  }

  if (servicesPerBene > 6.0) {
    insights.push({
      id: `INS-PRV-${provider.npi}-2`,
      title: `High Utilization Intensity Detected (${servicesPerBene.toFixed(1)} Services / Bene)`,
      category: 'Utilization Anomaly',
      summary: `Procedure billing density is 45% higher than peer provider averages within ${provider.providerType}.`,
      npi: provider.npi,
      providerName: provider.providerName,
      potentialDrivers: [
        'Frequent diagnostic follow-up visits',
        'Multiple routine lab tests per beneficiary encounter',
      ],
      suggestedAction: 'Audit repeat visit frequency and compare care pathway schedules with evidence-based clinical guidelines.',
      impactEstimate: '$280K Utilization Savings',
      confidenceScore: 0.88,
      isDemo: true,
      timestamp: 'Just now',
    });
  }

  if (insights.length === 0) {
    insights.push({
      id: `INS-PRV-${provider.npi}-3`,
      title: `Consistent Quality & Cost Alignment`,
      category: 'Contract Variance',
      summary: `${provider.providerName} demonstrates strong compliance with value-based benchmark thresholds across payment and risk metrics.`,
      npi: provider.npi,
      providerName: provider.providerName,
      potentialDrivers: ['Effective preventative care coordination', 'Balanced diagnostic testing frequency'],
      suggestedAction: 'Maintain current care management protocols and consider expanding beneficiary panel allocation.',
      impactEstimate: 'Benchmark Target Met',
      confidenceScore: 0.96,
      isDemo: true,
      timestamp: 'Just now',
    });
  }

  return insights;
}
