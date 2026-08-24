import { useEffect } from 'react';
import { useAIContext, AIContext } from '../context/AIContextContext';

// Lets any page publish structured context (page, route, selected ACO/year,
// visible KPIs, forecast, peer target, etc.) so the Global AI Assistant can
// answer questions grounded in exactly what the user is currently viewing.
export function usePageAIContext(context: AIContext, deps: any[] = []) {
  const { setAIContext } = useAIContext();

  const serializedCtx = JSON.stringify(context);

  useEffect(() => {
    setAIContext(context);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [serializedCtx, ...deps]);
}
