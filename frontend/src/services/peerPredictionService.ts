import { ApiResponse, DataMode } from '../types';
import { PeerPrediction, mockPeerPredictions } from '../data/mock/peerPredictionData';

export const peerPredictionService = {
  async getPeerPrediction(acoId: string, mode: DataMode): Promise<ApiResponse<PeerPrediction>> {
    if (mode === 'connected') {
      // REPLACE WITH FASTAPI PEER-PREDICTION MODEL ENDPOINT
      return { success: false, data: null as any, source: 'api', timestamp: new Date().toISOString() };
    }
    const data = mockPeerPredictions[acoId] || mockPeerPredictions['abc-aco'];
    return { success: true, data, source: 'demo', timestamp: new Date().toISOString() };
  }
};

export default peerPredictionService;
