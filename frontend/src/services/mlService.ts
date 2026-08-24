import { ApiResponse, MLPrediction, SimulationResult, DataMode } from '../types';
import { mockMLDataByACO } from '../data/mock/mlData';
import { apiService } from './apiService';

export const mlService = {
  async getMLPrediction(acoId: string, mode: DataMode): Promise<ApiResponse<MLPrediction>> {
    if (mode === 'connected') {
      const res = await apiService.request<MLPrediction>(`/predictions/${acoId}`);
      if (res.success && res.data) {
        return res;
      }
    }

    // DEMO DATA
    const data = mockMLDataByACO[acoId] || mockMLDataByACO['abc-aco'];
    return {
      success: true,
      data: data.prediction,
      source: 'demo',
      timestamp: new Date().toISOString()
    };
  },

  async runSimulation(
    acoId: string,
    inputs: {
      erReduction: number;
      readmissionReduction: number;
      preventiveImprovement: number;
      careCoordination: number;
      providerVariationReduction: number;
    },
    mode: DataMode
  ): Promise<ApiResponse<SimulationResult>> {
    if (mode === 'connected') {
      const res = await apiService.request<SimulationResult>('/simulator/run', 'POST', {
        aco_id: acoId,
        ...inputs,
      });
      if (res.success && res.data) {
        return res;
      }
    }

    // DEMO SIMULATION CALCULATION
    const baseData = mockMLDataByACO[acoId] || mockMLDataByACO['abc-aco'];
    const expectedVal = baseData.prediction.expectedValue;
    const outcome = baseData.prediction.predictedOutcome;
    
    const erImpact = (inputs.erReduction / 100) * 3000000;
    const readmissionImpact = (inputs.readmissionReduction / 100) * 2500000;
    const preventiveImpact = (inputs.preventiveImprovement / 100) * 1500000;
    const careCoordinationImpact = (inputs.careCoordination / 100) * 1200000;
    const providerVariationImpact = (inputs.providerVariationReduction / 100) * 2000000;
    
    const totalImpact = erImpact + readmissionImpact + preventiveImpact + careCoordinationImpact + providerVariationImpact;
    const projectedSavingsVal = outcome === 'GAIN' ? expectedVal + totalImpact : Math.max(0, expectedVal + totalImpact);
    const projectedLossVal = outcome === 'LOSS' ? Math.max(0, Math.abs(expectedVal) - totalImpact) : 0;
    
    const actualExpenditureBase = expectedVal < 0 ? Math.abs(expectedVal) * 10 : 100000000;
    const projectedExpenditure = Math.max(50000000, actualExpenditureBase - totalImpact);

    return {
      success: true,
      data: {
        projectedSavings: projectedSavingsVal,
        projectedLoss: projectedLossVal,
        projectedExpenditure,
        erImpact,
        readmissionImpact,
        careCoordinationImpact,
        providerVariationImpact,
        confidence: 88,
        source: 'demo'
      },
      source: 'demo',
      timestamp: new Date().toISOString()
    };
  }
};

