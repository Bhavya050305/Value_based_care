import { env } from '../../config/env';
import { ACORecord } from '../../types/aco';
import { transformCMSACORecord } from '../adapters/cmsAcoAdapter';
import { fetchMockACOs, fetchMockACOById } from '../mock/acoMockApi';

export async function getACOs(): Promise<ACORecord[]> {
  if (env.isMock) {
    return fetchMockACOs();
  }

  const response = await fetch(`${env.apiBaseUrl}/acos`);
  if (!response.ok) {
    throw new Error('Failed to fetch ACO records from backend API');
  }
  const rawData = await response.json();
  return rawData.map(transformCMSACORecord);
}

export async function getACOById(acoId: string): Promise<ACORecord | undefined> {
  if (env.isMock) {
    return fetchMockACOById(acoId);
  }

  const response = await fetch(`${env.apiBaseUrl}/acos/${acoId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch ACO ${acoId} from backend API`);
  }
  const rawData = await response.json();
  return transformCMSACORecord(rawData);
}
