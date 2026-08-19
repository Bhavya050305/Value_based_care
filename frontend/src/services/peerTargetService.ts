import { ApiResponse, DataMode } from '../types';
import { PeerTargetProfile, mockPeerTargets, getDefaultPeerTarget } from '../data/mock/peerTargetData';
import { apiService } from './apiService';

function normalizePeerTargetProfile(data: any): PeerTargetProfile {
  const target = data.target_aco || {};
  const rawPeers = Array.isArray(data.peers) ? data.peers : [];

  const similarPeers = rawPeers.map((p: any) => ({
    rank: p.rank || 0,
    acoId: p.aco_id || p.acoId || '',
    acoName: p.aco_name || p.acoName || '',
    savingsRate: p.savings_rate ?? p.savingsRate ?? 0,
    qualityScore: p.quality_score ?? p.qualityScore ?? 0,
    pmpm: p.pmpm ?? 0,
    similarityScore: p.similarity_score ?? p.similarityScore ?? 0,
    attributedMembers: p.attributed_members ?? p.attributedMembers ?? 0,
  }));

  return {
    acoId: data.aco_id || target.aco_id || 'A1001',
    acoName: target.aco_name || `ACO ${data.aco_id || 'A1001'}`,
    year: data.performance_year || target.performance_year || 2024,
    currentSavingsRate: target.current_savings_rate ?? 0,
    currentQuality: target.current_quality ?? 0,
    currentPMPM: target.current_pmpm ?? 0,
    targetSavingsRate: target.target_savings_rate ?? 0,
    targetQuality: target.target_quality ?? 0,
    targetPMPM: target.target_pmpm ?? 0,
    classification: target.classification || 'Mid Quartile',
    similarPeers,
    recommendation: data.recommendation || 'Focus on care coordination and ER deflection.',
    total: data.total ?? similarPeers.length,
    limit: data.limit ?? 20,
    offset: data.offset ?? 0,
    hasMore: data.has_more ?? data.hasMore ?? false,
  };
}

export const peerTargetService = {
  async getPeerTarget(
    acoId: string,
    mode: DataMode,
    year: number = 2024,
    limit: number = 20,
    offset: number = 0
  ): Promise<ApiResponse<PeerTargetProfile>> {
    if (mode === 'connected') {
      const res = await apiService.request<any>('/peer-target/find-peers', 'POST', {
        aco_id: acoId,
        performance_year: year,
        limit,
        offset,
      });
      if (res.success && res.data) {
        return {
          success: true,
          data: normalizePeerTargetProfile(res.data),
          source: 'api',
          timestamp: new Date().toISOString(),
        };
      }
    }
    return { success: true, data: getDefaultPeerTarget(acoId), source: 'demo', timestamp: new Date().toISOString() };
  },

  async listAvailableACOIds(mode: DataMode, year: number = 2024): Promise<ApiResponse<string[]>> {
    if (mode === 'connected') {
      const res = await apiService.request<string[]>(`/acos?year=${year}`);
      if (res.success && res.data && Array.isArray(res.data)) {
        return { success: true, data: (res.data as any[]).map((a: any) => a.id || a.aco_id), source: 'api', timestamp: new Date().toISOString() };
      }
    }
    return { success: true, data: Object.keys(mockPeerTargets), source: 'demo', timestamp: new Date().toISOString() };
  }
};

export default peerTargetService;


