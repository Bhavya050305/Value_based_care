import { useQuery } from '@tanstack/react-query';
import { getHospitals } from '../services/api/hospitalService';

export function useHospitals() {
  return useQuery({
    queryKey: ['hospitals'],
    queryFn: getHospitals,
    staleTime: 1000 * 60 * 5,
  });
}
