import React, { createContext, useContext, useState, ReactNode } from 'react';

// Structured context describing what the user is currently looking at.
// GlobalAIAssistant -> aiService -> FastAPI -> Structured Context -> Ollama -> Response
export interface AIContext {
  page: string;
  route: string;
  acoId?: string;
  acoName?: string;
  year?: number;
  [key: string]: any;
}

interface AIContextType {
  aiContext: AIContext;
  setAIContext: (ctx: AIContext) => void;
}

const defaultContext: AIContext = { page: 'Portfolio Overview', route: '/dashboard' };

const AIContextContext = createContext<AIContextType | undefined>(undefined);

export const AIContextProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [aiContext, setAIContextState] = useState<AIContext>(defaultContext);

  const setAIContext = (ctx: AIContext) => {
    setAIContextState((prev) => {
      try {
        if (JSON.stringify(prev) === JSON.stringify(ctx)) {
          return prev;
        }
      } catch (e) {
        // Fallthrough if non-serializable properties exist
      }
      return ctx;
    });
  };

  return (
    <AIContextContext.Provider value={{ aiContext, setAIContext }}>
      {children}
    </AIContextContext.Provider>
  );
};

export const useAIContext = (): AIContextType => {
  const context = useContext(AIContextContext);
  if (!context) {
    throw new Error('useAIContext must be used within an AIContextProvider');
  }
  return context;
};

export default AIContextContext;
