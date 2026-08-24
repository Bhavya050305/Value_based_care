import { ApiResponse, SHAPFeature, DataMode } from '../types';
import { mockMLDataByACO } from '../data/mock/mlData';
import { apiService } from './apiService';

export const shapService = {
  async getSHAPFeatures(acoId: string, mode: DataMode): Promise<ApiResponse<SHAPFeature[]>> {
    if (mode === 'connected') {
      const res = await apiService.request<any>(`/acos/${acoId}/drivers`);
      if (res.success && res.data) {
        const driversList = Array.isArray(res.data) ? res.data : (res.data.shap_features || res.data.features || []);
        if (driversList.length > 0) {
          return {
            ...res,
            data: driversList
          };
        }
      }
    }

    // DEMO DATA
    const data = mockMLDataByACO[acoId] || mockMLDataByACO['abc-aco'];
    return {
      success: true,
      data: data.shapFeatures,
      source: 'demo',
      timestamp: new Date().toISOString()
    };
  }
};

