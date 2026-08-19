import { ApiResponse, ACO, DataMode } from '../types';
import { mockACOs } from '../data/mock/acoData';
import { apiService } from './apiService';

function normalizeAco(item: any): ACO {
  return {
    id: item.aco_id || item.id,
    name: item.name || item.aco_name || `ACO ${item.aco_id || item.id}`,
    riskLevel: item.risk_level || (item.savings_loss && item.savings_loss < 0 ? 'HIGH' : 'LOW'),
    attributedMembers: item.attributed_members ?? item.beneficiaries ?? 0,
    riskAdjustedBenchmarkPMPM: item.benchmark_pmpm ?? 0,
    actualPMPM: item.pmpm ?? 0,
    savingsLoss: item.savings_loss ?? 0,
    savingsLossPercent: item.savings_loss_pct ?? 0,
    qualityScore: item.quality_score ?? item.qual_score ?? 0,
    totalExpenditure: item.total_expenditure ?? 0,
    trend: item.trend || [],
    agreementType: item.agreement_type || 'Standard',
    track: item.track || 'MSSP Track 1+',
    startYear: item.start_year || 2021,
    benchmarkMethod: item.benchmark_method || 'CMS Regional Historical',
    riskModel: item.risk_model || 'Two-Sided Risk',
    riskScoreModel: item.risk_score_model || 'CMS-HCC Risk Adjustment',
    topDriver: item.top_driver || 'Expenditure Variance',
    topProviderIssue: item.top_provider_issue || 'Care Coordination',
    predictedOutcome: item.predicted_outcome || (item.savings_loss && item.savings_loss < 0 ? 'LOSS' : 'GAIN'),
    riskProbability: item.risk_probability || 50,
  };
}

export const acoService = {
  async getACOs(mode: DataMode, year: number = 2024): Promise<ApiResponse<ACO[]>> {
    if (mode === 'connected') {
      const targetYear = year || 2024;
      const endpoint = `/acos?year=${targetYear}`;
      const res = await apiService.request<any[]>(endpoint);
      if (res.success && res.data && Array.isArray(res.data) && res.data.length > 0) {
        return {
          success: true,
          data: res.data.map(normalizeAco),
          source: 'api',
          timestamp: new Date().toISOString(),
        };
      }
      return {
        success: false,
        message: "No ACO data found.",
        data: [],
        source: 'api',
        timestamp: new Date().toISOString(),
      };
    }

    return {
      success: true,
      data: mockACOs,
      source: 'demo',
      timestamp: new Date().toISOString()
    };
  },

  async getACOById(id: string, mode: DataMode, year: number = 2024): Promise<ApiResponse<ACO>> {
    const cleanId = (id || '').trim();
    const targetYear = year || 2024;

    if (mode === 'connected') {
      const endpoint = `/acos/${encodeURIComponent(cleanId)}?year=${targetYear}`;
      const res = await apiService.request<any>(endpoint);
      if (res.success && res.data) {
        return {
          success: true,
          data: normalizeAco(res.data),
          source: 'api',
          timestamp: new Date().toISOString(),
        };
      }
      return {
        success: false,
        message: `ACO with ID '${cleanId}' was not found.`,
        data: null as any,
        source: 'api',
        timestamp: new Date().toISOString(),
      };
    }

    const aco = mockACOs.find(a => a.id.toLowerCase() === cleanId.toLowerCase() || a.name.toLowerCase() === cleanId.toLowerCase());
    if (!aco) {
      return {
        success: false,
        message: `ACO with ID '${cleanId}' was not found.`,
        data: null as any,
        source: 'demo',
        timestamp: new Date().toISOString()
      };
    }

    return {
      success: true,
      data: aco,
      source: 'demo',
      timestamp: new Date().toISOString()
    };
  }
};
