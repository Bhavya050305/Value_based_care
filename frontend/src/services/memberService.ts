import { ApiResponse, MemberRisk, DataMode } from '../types';
import { mockMemberRiskByACO } from '../data/mock/memberData';
import { apiService } from './apiService';

export const memberService = {
  async getMemberRisk(acoId: string, mode: DataMode): Promise<ApiResponse<MemberRisk>> {
    if (mode === 'connected') {
      const res = await apiService.request<MemberRisk>(`/members/risk?acoId=${acoId}`);
      if (res.success && res.data) {
        return res;
      }
    }

    // DEMO DATA
    const data = mockMemberRiskByACO[acoId] || mockMemberRiskByACO['abc-aco'];
    return {
      success: true,
      data,
      source: 'demo',
      timestamp: new Date().toISOString()
    };
  }
};
