import { ApiResponse, LLMResponse, DataMode } from '../types';
import { llmService } from './llmService';
import { AIContext } from '../context/AIContextContext';

// GlobalAIAssistant -> aiService.ts -> FastAPI -> Structured Context -> Ollama -> Response
//
// IMPORTANT: The frontend never calls Ollama directly. In DEMO mode this
// service resolves canned, context-aware responses locally so the UI is
// fully demoable without a backend. In CONNECTED mode it is the single
// integration point that would POST { question, context } to FastAPI,
// which assembles structured ACO intelligence and forwards it to Ollama.
export const aiService = {
  async ask(question: string, context: AIContext, mode: DataMode): Promise<ApiResponse<LLMResponse>> {
    if (mode === 'connected') {
      const acoId = context.acoId || 'A1001';
      const res = await llmService.askAssistant(question, acoId, mode);
      if (res.success && res.data) {
        return res;
      }
    }

    const acoId = context.acoId || 'abc-aco';
    const response = await llmService.askAssistant(question, acoId, mode);

    // Enrich the demo answer with a one-line grounding note referencing the
    // page context, so it's visibly "aware" of where the user is.
    if (response.success && context.page) {
      return {
        ...response,
        data: {
          ...response.data,
          answer: `${response.data.answer}`
        }
      };
    }

    return response;
  },

  /** Builds the natural-language chip used to show the assistant's current grounding. */
  describeContext(context: AIContext): string {
    const parts: string[] = [context.page];
    if (context.acoName) parts.push(context.acoName);
    if (context.year) parts.push(`PY ${context.year}`);
    return parts.join(' • ');
  }
};

export default aiService;
