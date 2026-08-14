import { useQuery } from '@tanstack/react-query';
import { getACOs } from '../services/api/acoService';

export function useACOs() {
  return useQuery({
    queryKey: ['acos'],
    queryFn: getACOs,
    staleTime: 1000 * 60 * 5,
  });
}
