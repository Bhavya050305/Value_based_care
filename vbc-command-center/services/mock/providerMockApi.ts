import { ProviderRecord } from '../../types/provider';
import { PortfolioSummary, HistoricalTrendPoint } from '../../types/metrics';
import { mockProviders } from '../../data/mock/providers';

export async function fetchMockProviders(): Promise<ProviderRecord[]> {
  // Simulate standard network delay
  await new Promise((resolve) => setTimeout(resolve, 150));
  return mockProviders;
}

export async function fetchMockProviderByNpi(npi: string): Promise<ProviderRecord | undefined> {
  await new Promise((resolve) => setTimeout(resolve, 100));
  return mockProviders.find((p) => p.npi === npi);
}

export async function fetchMockPortfolioSummary(): Promise<PortfolioSummary> {
  await new Promise((resolve) => setTimeout(resolve, 100));

  const totalProviders = mockProviders.length;
  const totalBeneficiaries = mockProviders.reduce((acc, p) => acc + p.totalBeneficiaries, 0);
  const totalMedicarePayments = mockProviders.reduce((acc, p) => acc + p.totalMedicarePaymentAmount, 0);
  const totalMedicareAllowed = mockProviders.reduce((acc, p) => acc + p.totalMedicareAllowedAmount, 0);
  const totalServices = mockProviders.reduce((acc, p) => acc + p.totalServices, 0);
  const totalStandardizedAmount = mockProviders.reduce((acc, p) => acc + p.totalMedicareStandardizedAmount, 0);

  const averageBeneficiaryAge = Number(
    (mockProviders.reduce((acc, p) => acc + p.averageBeneficiaryAge * p.totalBeneficiaries, 0) / totalBeneficiaries).toFixed(1)
  );

  const averageRiskScore = Number(
    (mockProviders.reduce((acc, p) => acc + p.averageRiskScore * p.totalBeneficiaries, 0) / totalBeneficiaries).toFixed(2)
  );

  return {
    totalProviders,
    totalBeneficiaries,
    totalMedicarePayments,
    totalMedicareAllowed,
    totalServices,
    averageBeneficiaryAge,
    averageRiskScore,
    totalStandardizedAmount,
    paymentChangePct: 6.4,
    allowedChangePct: 5.8,
    beneficiariesChangePct: 4.2,
    servicesChangePct: 3.1,
    riskScoreChangePct: 1.5,
  };
}

export async function fetchMockHistoricalTrends(): Promise<HistoricalTrendPoint[]> {
  return [
    { year: '2020', allowedAmount: 38200000, paymentAmount: 31200000, standardizedAmount: 29800000, isDemo: true },
    { year: '2021', allowedAmount: 41500000, paymentAmount: 33800000, standardizedAmount: 32100000, isDemo: true },
    { year: '2022', allowedAmount: 45200000, paymentAmount: 36900000, standardizedAmount: 35100000, isDemo: true },
    { year: '2023', allowedAmount: 48900000, paymentAmount: 39900000, standardizedAmount: 37900000, isDemo: true },
    { year: '2024', allowedAmount: 53200000, paymentAmount: 43260000, standardizedAmount: 40410000, isDemo: true },
  ];
}
