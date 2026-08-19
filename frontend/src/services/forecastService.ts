import { ApiResponse, DataMode } from '../types';
import { ACOForecast, mockACOForecasts, mockPortfolioForecast } from '../data/mock/forecastData';
import { apiService } from './apiService';

export const forecastService = {
  async getACOForecast(acoId: string, mode: DataMode): Promise<ApiResponse<any>> {
    if (mode === 'connected') {
      const res = await apiService.request<any>(`/predictions/forecast/${acoId}`);
      if (res.success && res.data && res.data.combined_series) {
        return res;
      }
    }
    const data = mockACOForecasts[acoId] || mockACOForecasts['abc-aco'];
    return { success: true, data, source: 'demo', timestamp: new Date().toISOString() };
  },

  async getPortfolioForecast(mode: DataMode): Promise<ApiResponse<ACOForecast>> {
    if (mode === 'connected') {
      const res = await apiService.request<any>('/predictions');
      if (res.success && res.data && res.data.series) {
        return res;
      }
    }
    return { success: true, data: mockPortfolioForecast, source: 'demo', timestamp: new Date().toISOString() };
  }
};

export default forecastService;

