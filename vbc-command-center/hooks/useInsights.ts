import { useQuery } from '@tanstack/react-query';
import { getPortfolioInsights } from '../services/insights/insightEngine';

export function useInsights() {
  return useQuery({
    queryKey: ['insights'],
    queryFn: getPortfolioInsights,
    staleTime: 1000 * 60 * 5,
  });
}
