// Environment Configuration for Phase 1 (Mock) and Phase 2 (Backend API) Integration

export const ENV = {
  dataSource: (import.meta.env.VITE_DATA_SOURCE as 'mock' | 'api') || 'mock',
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  appVersion: '2.4.0',
  isMock: (import.meta.env.VITE_DATA_SOURCE as string) !== 'api',
  isDemoMode: (import.meta.env.VITE_DATA_SOURCE as string) !== 'api',
  lastUpdatedDate: 'Aug 13, 2026',
};

// Legacy lowercase alias for existing service adapters
export const env = ENV;
