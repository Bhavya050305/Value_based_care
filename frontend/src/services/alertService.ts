import { ApiResponse, DataMode } from '../types';
import { Alert, AnomalyAlertsResponseData } from '../types';
import { mockAlerts } from '../data/mock/alertsData';
import { apiService } from './apiService';

export const alertService = {
  async getAlerts(year: number, mode: DataMode = 'connected'): Promise<ApiResponse<AnomalyAlertsResponseData>> {
    if (mode === 'connected') {
      try {
        const res = await apiService.request<any>(`/portfolio/alerts?year=${year}`);
        if (res.success && res.data && res.data.alerts) {
          const rawAlerts = res.data.alerts || [];
          const mappedAlerts: Alert[] = rawAlerts.map((item: any) => ({
            id: item.id || `alert-${year}-${item.aco_id}`,
            severity: (item.severity || 'LOW') as 'HIGH' | 'MEDIUM' | 'LOW' | 'NORMAL',
            date: `${year}-08-18`,
            aco: item.aco_name || item.aco_id,
            acoId: item.aco_id,
            metric: item.metric || 'Anomaly Signature',
            explanation: item.explanation || 'Anomaly detected based on feature inputs.',
            recommendedAction: item.recommended_action || 'Review clinical and financial performance.',
            status: (item.status || 'active') as 'active' | 'reviewed',
            score: item.score,
            performanceYear: item.performance_year || year,
            savingsLoss: item.savings_loss,
            features: item.features,
          }));

          return {
            success: true,
            data: {
              performance_year: res.data.performance_year || year,
              total_acos: res.data.total_acos || mappedAlerts.length,
              counts: res.data.counts || {
                total: mappedAlerts.length,
                high: mappedAlerts.filter((a) => a.severity === 'HIGH').length,
                medium: mappedAlerts.filter((a) => a.severity === 'MEDIUM').length,
                low: mappedAlerts.filter((a) => a.severity === 'LOW').length,
                normal: mappedAlerts.filter((a) => a.severity === 'NORMAL').length,
              },
              alerts: mappedAlerts,
            },
            source: 'database',
            timestamp: new Date().toISOString(),
          };
        }
      } catch (err) {
        console.error('[alertService] Error fetching portfolio alerts:', err);
      }
    }

    // Demo fallback
    return {
      success: true,
      data: {
        performance_year: year,
        total_acos: mockAlerts.length,
        counts: {
          total: mockAlerts.length,
          high: mockAlerts.filter((a) => a.severity === 'HIGH').length,
          medium: mockAlerts.filter((a) => a.severity === 'MEDIUM').length,
          low: mockAlerts.filter((a) => a.severity === 'LOW').length,
          normal: 0,
        },
        alerts: mockAlerts,
      },
      source: 'demo',
      timestamp: new Date().toISOString(),
    };
  },
};

export default alertService;
