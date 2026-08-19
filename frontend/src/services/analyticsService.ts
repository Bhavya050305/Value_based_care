import { ApiResponse, DataMode } from '../types';
import { PortfolioSummary, FinancialTrendPoint, ACOFinancialTrendPoint, mockPortfolioSummary, mockPortfolioFinancialTrend, mockACOFinancialTrend } from '../data/mock/financialData';
import { QualityTrendPoint, mockQualityByACO } from '../data/mock/qualityData';
import { apiService } from './apiService';

function normalizeSummary(data: any): PortfolioSummary {
  const total = data.total_acos ?? data.totalACOs ?? 0;
  const good = data.goodStanding ?? data.good_standing ?? 0;
  const attention = data.needsAttention ?? data.needs_attention ?? 0;
  const risk = data.atRisk ?? data.at_risk ?? 0;
  const totalSavings = data.totalSavings ?? data.total_savings ?? data.net_savings_loss ?? 0;
  const totalLoss = data.totalLoss ?? data.total_loss ?? 0;
  const totalExpenditure = data.totalExpenditure ?? data.total_expenditure ?? data.total_actual_expenditure ?? 0;
  const riskAdjustedBenchmark = data.riskAdjustedBenchmark ?? data.risk_adjusted_benchmark ?? data.total_benchmark_expenditure ?? 0;
  const riskAdjustmentImpact = data.riskAdjustmentImpact ?? data.risk_adjustment_impact ?? 0;

  return {
    totalACOs: total,
    goodStanding: good,
    needsAttention: attention,
    atRisk: risk,
    totalSavings,
    totalLoss,
    totalExpenditure,
    riskAdjustedBenchmark,
    riskAdjustmentImpact,
  };
}

export const analyticsService = {
  async getPortfolioSummary(mode: DataMode, year: number): Promise<ApiResponse<PortfolioSummary>> {
    if (mode === 'connected') {
      const res = await apiService.request<any>(`/dashboard/summary?year=${year}`);
      if (res.success && res.data) {
        return {
          success: true,
          data: normalizeSummary(res.data),
          source: 'api',
          timestamp: new Date().toISOString(),
        };
      }
      return {
        success: false,
        message: "No portfolio data found for selected performance year.",
        data: null as any,
        source: 'api',
        timestamp: new Date().toISOString()
      };
    }

    return {
      success: true,
      data: mockPortfolioSummary,
      source: 'demo',
      timestamp: new Date().toISOString()
    };
  },

  async getPortfolioFinancialTrend(mode: DataMode): Promise<ApiResponse<FinancialTrendPoint[]>> {
    if (mode === 'connected') {
      const res = await apiService.request<any[]>('/portfolio/trends');
      if (res.success && res.data && Array.isArray(res.data) && res.data.length > 0) {
        const trends: FinancialTrendPoint[] = res.data.map((pt: any) => ({
          year: pt.performance_year || pt.year || 2024,
          savings: pt.gross_savings_loss ?? pt.savings ?? 0,
          loss: pt.loss ?? 0,
          actualExpenditure: pt.actual_expenditure ?? pt.actualExpenditure ?? 0,
          benchmarkExpenditure: pt.benchmark_expenditure ?? pt.benchmarkExpenditure ?? 0,
        }));
        return {
          success: true,
          data: trends,
          source: 'api',
          timestamp: new Date().toISOString(),
        };
      }
      return {
        success: false,
        message: "No portfolio trend data found.",
        data: [],
        source: 'api',
        timestamp: new Date().toISOString()
      };
    }

    return {
      success: true,
      data: mockPortfolioFinancialTrend,
      source: 'demo',
      timestamp: new Date().toISOString()
    };
  },

  async getACOFinancialTrend(acoId: string, mode: DataMode, year: number): Promise<ApiResponse<ACOFinancialTrendPoint[]>> {
    const cleanId = (acoId || '').trim();
    if (mode === 'connected') {
      const res = await apiService.request<any>(`/acos/${encodeURIComponent(cleanId)}/financial?year=${year}`);
      if (res.success && res.data) {
        const d = res.data;
        const trendPoint: ACOFinancialTrendPoint = {
          year: d.performance_year || year,
          actualExpenditure: d.actual_expenditure || 0,
          benchmarkExpenditure: d.benchmark_expenditure || 0,
          savings: d.gross_savings_loss || 0,
        };
        return {
          success: true,
          data: [trendPoint],
          source: 'api',
          timestamp: new Date().toISOString()
        };
      }
      return {
        success: false,
        message: `No financial data found for ACO '${cleanId}' in year ${year}.`,
        data: [],
        source: 'api',
        timestamp: new Date().toISOString()
      };
    }

    const data = mockACOFinancialTrend[cleanId] || mockACOFinancialTrend['abc-aco'];
    return {
      success: true,
      data,
      source: 'demo',
      timestamp: new Date().toISOString()
    };
  },

  async getACOQualityTrend(acoId: string, mode: DataMode, year: number): Promise<ApiResponse<QualityTrendPoint[]>> {
    const cleanId = (acoId || '').trim();
    if (mode === 'connected') {
      const res = await apiService.request<any>(`/acos/${encodeURIComponent(cleanId)}/quality?year=${year}`);
      if (res.success && res.data) {
        const d = res.data;
        const qPoint: QualityTrendPoint = {
          year: d.performance_year || year,
          qualityScore: d.quality_score ?? 0,
          preventiveCareRate: 0,
          readmissionRate: 0,
        };
        return {
          success: true,
          data: [qPoint],
          source: 'api',
          timestamp: new Date().toISOString()
        };
      }
      return {
        success: false,
        message: `No quality data found for ACO '${cleanId}' in year ${year}.`,
        data: [],
        source: 'api',
        timestamp: new Date().toISOString()
      };
    }

    const data = mockQualityByACO[cleanId] || mockQualityByACO['abc-aco'];
    return {
      success: true,
      data,
      source: 'demo',
      timestamp: new Date().toISOString()
    };
  }
};
