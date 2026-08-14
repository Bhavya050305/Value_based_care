import { HospitalRecord } from '../../types/hospital';
import { mockHospitals } from '../../data/mock/hospitals';

export async function fetchMockHospitals(): Promise<HospitalRecord[]> {
  await new Promise((resolve) => setTimeout(resolve, 150));
  return mockHospitals;
}
