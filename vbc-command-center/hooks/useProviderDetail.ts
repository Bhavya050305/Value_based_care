import { useQuery } from '@tanstack/react-query';
import { getProviderByNpi } from '../services/api/providerService';

export function useProviderDetail(npi: string | undefined) {
  return useQuery({
    queryKey: ['providerDetail', npi],
    queryFn: () => (npi ? getProviderByNpi(npi) : Promise.resolve(undefined)),
    enabled: Boolean(npi),
    staleTime: 1000 * 60 * 5,
  });
}
