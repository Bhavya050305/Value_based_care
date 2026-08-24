import { ApiResponse, Provider, DataMode } from '../types';
import { mockProvidersByACO, defaultProviders } from '../data/mock/providerData';
import { apiService } from './apiService';

export const providerService = {
  async getProviders(acoId: string, mode: DataMode): Promise<ApiResponse<Provider[]>> {
    if (mode === 'connected') {
      const res = await apiService.request<Provider[]>(`/acos/${acoId}/providers`);
      if (res.success && res.data && res.data.length > 0) {
        return res;
      }
    }

    // DEMO DATA
    const data = mockProvidersByACO[acoId] || defaultProviders;
    return {
      success: true,
      data,
      source: 'demo',
      timestamp: new Date().toISOString()
    };
  }
};

