import { ProviderRecord } from '../types/provider';

/**
 * Configurable business rule utility for provider performance tier calculation.
 * Can easily be overridden or replaced by backend / ML classification in Phase 2.
 */
export function calculateProviderPerformance(provider: Partial<ProviderRecord>): 'High Performance' | 'Moderate' | 'Needs Attention' {
  const riskScore = provider.averageRiskScore || 1.0;
  const servicesPerBene = (provider.totalServices && provider.totalBeneficiaries)
    ? provider.totalServices / provider.totalBeneficiaries
    : 4.0;
  const paymentPerBene = (provider.totalMedicarePaymentAmount && provider.totalBeneficiaries)
    ? provider.totalMedicarePaymentAmount / provider.totalBeneficiaries
    : 1000;
  
  // High risk or extreme utilization relative to payment
  if (riskScore > 1.4 || servicesPerBene > 8.5 || paymentPerBene > 2800) {
    return 'Needs Attention';
  }
  
  // High efficiency relative to risk score
  if (riskScore <= 1.1 && servicesPerBene <= 4.5 && paymentPerBene <= 1200) {
    return 'High Performance';
  }

  return 'Moderate';
}
