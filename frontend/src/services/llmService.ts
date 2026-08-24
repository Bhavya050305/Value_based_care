import { ApiResponse, AIExplanation, LLMResponse, DataMode } from '../types';
import { getRiskExplanationLLM, getDriverExplanationLLM, getRecommendationsLLM, getAssistantAnswerLLM } from '../data/mock/llmResponses';
import { apiService } from './apiService';

export const llmService = {
  async getRiskExplanation(acoId: string, mode: DataMode): Promise<ApiResponse<AIExplanation>> {
    if (mode === 'connected') {
      const res = await apiService.request<AIExplanation>('/assistant/prompt', 'POST', {
        aco_id: acoId,
        prompt_type: 'risk_explanation',
      });
      if (res.success && res.data) {
        return res;
      }
    }

    // DEMO DATA
    return {
      success: true,
      data: getRiskExplanationLLM(acoId),
      source: 'demo',
      timestamp: new Date().toISOString()
    };
  },

  async getDriverExplanation(acoId: string, driver: string, mode: DataMode): Promise<ApiResponse<AIExplanation>> {
    if (mode === 'connected') {
      const res = await apiService.request<AIExplanation>('/assistant/prompt', 'POST', {
        aco_id: acoId,
        driver,
        prompt_type: 'driver_explanation',
      });
      if (res.success && res.data) {
        return res;
      }
    }

    // DEMO DATA
    return {
      success: true,
      data: getDriverExplanationLLM(acoId, driver),
      source: 'demo',
      timestamp: new Date().toISOString()
    };
  },

  async getRecommendations(acoId: string, mode: DataMode): Promise<ApiResponse<AIExplanation>> {
    if (mode === 'connected') {
      const res = await apiService.request<AIExplanation>('/assistant/prompt', 'POST', {
        aco_id: acoId,
        prompt_type: 'recommendations',
      });
      if (res.success && res.data) {
        return res;
      }
    }

    // DEMO DATA
    return {
      success: true,
      data: getRecommendationsLLM(acoId),
      source: 'demo',
      timestamp: new Date().toISOString()
    };
  },

  async askAssistant(question: string, acoId: string, mode: DataMode, year?: number): Promise<ApiResponse<LLMResponse>> {
    if (mode === 'connected') {
      const res = await apiService.request<LLMResponse>('/assistant/chat', 'POST', {
        message: question,
        aco_id: acoId,
        year: year || 2024,
      });
      if (res.success && res.data) {
        return res;
      }
    }

    // Resolve question key from questions list
    let questionKey = 'generic';
    const lowerQ = question.toLowerCase();
    
    if (lowerQ.includes('risk') || lowerQ.includes('predicted')) {
      questionKey = 'why_at_risk';
    } else if (lowerQ.includes('driver') || lowerQ.includes('utilization')) {
      questionKey = 'main_drivers';
    } else if (lowerQ.includes('variation') || lowerQ.includes('provider')) {
      questionKey = 'highest_variation';
    } else if (lowerQ.includes('payer') || lowerQ.includes('do') || lowerQ.includes('action')) {
      questionKey = 'payer_actions';
    }

    // DEMO DATA
    return {
      success: true,
      data: getAssistantAnswerLLM(questionKey, acoId),
      source: 'demo',
      timestamp: new Date().toISOString()
    };
  }
};

