import { ACORecord } from '../../types/aco';
import { mockACOs } from '../../data/mock/acos';

export async function fetchMockACOs(): Promise<ACORecord[]> {
  await new Promise((resolve) => setTimeout(resolve, 150));
  return mockACOs;
}

export async function fetchMockACOById(acoId: string): Promise<ACORecord | undefined> {
  await new Promise((resolve) => setTimeout(resolve, 100));
  return mockACOs.find((a) => a.acoId === acoId);
}
