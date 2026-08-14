import { env } from '../../config/env';
import { HospitalRecord } from '../../types/hospital';
import { transformHVBPRecord } from '../adapters/hvbpAdapter';
import { fetchMockHospitals } from '../mock/hospitalMockApi';

export async function getHospitals(): Promise<HospitalRecord[]> {
  if (env.isMock) {
    return fetchMockHospitals();
  }

  const response = await fetch(`${env.apiBaseUrl}/hospitals`);
  if (!response.ok) {
    throw new Error('Failed to fetch hospital quality safety records from backend API');
  }
  const rawData = await response.json();
  return rawData.map(transformHVBPRecord);
}
