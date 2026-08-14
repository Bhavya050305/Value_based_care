import { env } from '../../config/env';
import { ProviderRecord } from '../../types/provider';
import { PortfolioSummary, HistoricalTrendPoint } from '../../types/metrics';
import { transformCMSProviderRecord } from '../adapters/cmsProviderAdapter';
import {
  fetchMockProviders,
  fetchMockProviderByNpi,
  fetchMockPortfolioSummary,
  fetchMockHistoricalTrends,
} from '../mock/providerMockApi';

export async function getProviders(): Promise<ProviderRecord[]> {
  if (env.isMock) {
    return fetchMockProviders();
  }
  
  // Real Backend Integration (Phase 2)
  const response = await fetch(`${env.apiBaseUrl}/providers`);
  if (!response.ok) {
    throw new Error('Failed to fetch provider records from backend API');
  }
  const rawData = await response.json();
  return rawData.map(transformCMSProviderRecord);
}

export async function getProviderByNpi(npi: string): Promise<ProviderRecord | undefined> {
  if (env.isMock) {
    return fetchMockProviderByNpi(npi);
  }

  const response = await fetch(`${env.apiBaseUrl}/providers/${npi}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch provider NPI ${npi} from backend API`);
  }
  const rawData = await response.json();
  return transformCMSProviderRecord(rawData);
}

export async function getPortfolioSummary(): Promise<PortfolioSummary> {
  if (env.isMock) {
    return fetchMockPortfolioSummary();
  }

  const response = await fetch(`${env.apiBaseUrl}/portfolio/summary`);
  if (!response.ok) {
    throw new Error('Failed to fetch portfolio summary from backend API');
  }
  return response.json();
}

export async function getHistoricalTrends(): Promise<HistoricalTrendPoint[]> {
  if (env.isMock) {
    return fetchMockHistoricalTrends();
  }

  const response = await fetch(`${env.apiBaseUrl}/portfolio/trends`);
  if (!response.ok) {
    throw new Error('Failed to fetch historical trends from backend API');
  }
  return response.json();
}
