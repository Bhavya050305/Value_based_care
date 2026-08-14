import { useQuery } from '@tanstack/react-query';
import { mockAlerts } from '../data/mock/alertsData';

export function useAlerts() {
  return useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      await new Promise((res) => setTimeout(res, 100));
      return mockAlerts;
    },
    staleTime: 1000 * 60 * 5,
  });
}
