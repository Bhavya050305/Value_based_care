import { useQuery } from '@tanstack/react-query';
import { getProviders, getPortfolioSummary, getHistoricalTrends } from '../services/api/providerService';
import { useFilterStore } from '../store/filterStore';

export function useProviders() {
  const { state, providerType, riskLevel, performanceTier, searchQuery } = useFilterStore();

  const query = useQuery({
    queryKey: ['providers'],
    queryFn: getProviders,
    staleTime: 1000 * 60 * 5,
  });

  const filteredProviders = (query.data || []).filter((p) => {
    if (state !== 'All' && p.state !== state) return false;
    if (providerType !== 'All' && p.providerType !== providerType) return false;
    if (performanceTier !== 'All' && p.performanceTier !== performanceTier) return false;
    if (riskLevel !== 'All') {
      if (riskLevel === 'High Risk' && p.averageRiskScore <= 1.4) return false;
      if (riskLevel === 'Moderate Risk' && (p.averageRiskScore < 1.1 || p.averageRiskScore > 1.4)) return false;
      if (riskLevel === 'Low Risk' && p.averageRiskScore >= 1.1) return false;
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchName = p.providerName.toLowerCase().includes(q);
      const matchNpi = p.npi.includes(q);
      const matchType = p.providerType.toLowerCase().includes(q);
      const matchState = p.state.toLowerCase().includes(q);
      if (!matchName && !matchNpi && !matchType && !matchState) return false;
    }
    return true;
  });

  return {
    ...query,
    providers: filteredProviders,
    allProviders: query.data || [],
  };
}

export function usePortfolioSummary() {
  return useQuery({
    queryKey: ['portfolioSummary'],
    queryFn: getPortfolioSummary,
    staleTime: 1000 * 60 * 5,
  });
}

export function useHistoricalTrends() {
  return useQuery({
    queryKey: ['historicalTrends'],
    queryFn: getHistoricalTrends,
    staleTime: 1000 * 60 * 5,
  });
}
