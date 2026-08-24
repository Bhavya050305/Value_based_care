import React, { useState, useEffect, useRef } from 'react';
import { useACO, SUPPORTED_YEARS } from '../context/ACOContext';
import { useDataMode } from '../context/DataModeContext';
import { usePageAIContext } from '../hooks/usePageAIContext';
import { Layout } from '../components/Layout';
import { llmService } from '../services/llmService';
import {
  Sparkles,
  Send,
  Loader2,
  Bot,
  User,
  Trash2,
  Building,
  Calendar,
  ShieldCheck,
  Lightbulb
} from 'lucide-react';

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  keyFactors?: string[];
  recommendedAction?: string;
  sourceData?: string;
  acoId?: string;
  year?: number;
  timestamp: Date;
}

export const AIAssistantPage: React.FC = () => {
  const { dataMode } = useDataMode();
  const { availableAcos, selectedAcoId, setSelectedAcoId, selectedYear, setSelectedYear } = useACO();

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const activeAcoId = selectedAcoId || (availableAcos[0]?.aco_id || availableAcos[0]?.id || 'A1001');
  const activeAcoName = availableAcos.find(a => (a.aco_id || a.id) === activeAcoId)?.name || `ACO ${activeAcoId}`;

  usePageAIContext(
    {
      page: 'AI Assistant',
      route: '/ai-assistant',
      acoId: activeAcoId,
      year: selectedYear,
    },
    [activeAcoId, selectedYear]
  );

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (queryText?: string) => {
    const q = (queryText || inputQuery).trim();
    if (!q || loading) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: q,
      acoId: activeAcoId,
      year: selectedYear,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    if (!queryText) setInputQuery('');
    setLoading(true);

    try {
      const res = await llmService.askAssistant(q, activeAcoId, dataMode, selectedYear);
      if (res.success && res.data) {
        const botMsg: ChatMessage = {
          id: `bot-${Date.now()}`,
          sender: 'assistant',
          text: res.data.answer || 'No direct answer returned.',
          keyFactors: res.data.keyFactors,
          recommendedAction: res.data.recommendedAction,
          sourceData: res.data.sourceData || `Supabase Analytics Engine (PY ${selectedYear})`,
          acoId: activeAcoId,
          year: selectedYear,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, botMsg]);
      } else {
        setMessages(prev => [
          ...prev,
          {
            id: `err-${Date.now()}`,
            sender: 'assistant',
            text: res.message || 'I could not retrieve performance data for that query.',
            timestamp: new Date()
          }
        ]);
      }
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: 'assistant',
          text: 'An error occurred while analyzing performance data. Please try again.',
          timestamp: new Date()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <Layout title="ACO Performance Intelligence Assistant" onLogout={() => {}}>
      <div className="flex flex-col h-[calc(100vh-8.5rem)] bg-white rounded-xl border border-vbc-gray-light shadow-card overflow-hidden">
        {/* Header Controls Bar */}
        <div className="bg-slate-900 text-white px-6 py-3.5 flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 shrink-0">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-vbc-blue/20 rounded-lg text-vbc-blue-light border border-vbc-blue/30">
              <Sparkles size={18} />
            </div>
            <div>
              <h2 className="font-bold text-sm text-white flex items-center space-x-2">
                <span>ACO Performance Intelligence Assistant</span>
              </h2>
              <p className="text-[11px] text-slate-400">
                Data-Grounded Strategic Intelligence • Supabase PostgreSQL Connected
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-xs">
            {/* ACO Selector */}
            <div className="flex items-center space-x-1.5 bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1 text-slate-300">
              <Building size={13} className="text-vbc-blue-light shrink-0" />
              <select
                value={activeAcoId}
                onChange={(e) => setSelectedAcoId(e.target.value)}
                className="bg-transparent text-white font-semibold focus:outline-none max-w-[180px] truncate cursor-pointer"
              >
                {availableAcos.length > 0 ? (
                  availableAcos.map((a) => (
                    <option key={a.aco_id || a.id} value={a.aco_id || a.id} className="bg-slate-900 text-white">
                      {a.name || a.aco_id || a.id} ({a.aco_id || a.id})
                    </option>
                  ))
                ) : (
                  <option value={activeAcoId} className="bg-slate-900 text-white">{activeAcoId}</option>
                )}
              </select>
            </div>

            {/* Performance Year Selector */}
            <div className="flex items-center space-x-1.5 bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1 text-slate-300">
              <Calendar size={13} className="text-vbc-blue-light shrink-0" />
              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(Number(e.target.value))}
                className="bg-transparent text-white font-semibold focus:outline-none cursor-pointer"
              >
                {SUPPORTED_YEARS.map((y) => (
                  <option key={y} value={y} className="bg-slate-900 text-white">
                    PY {y}
                  </option>
                ))}
              </select>
            </div>

            {/* Clear Chat Button */}
            {messages.length > 0 && (
              <button
                onClick={clearChat}
                className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors flex items-center space-x-1"
                title="Clear conversation history"
              >
                <Trash2 size={16} />
                <span className="hidden sm:inline text-[11px]">Clear</span>
              </button>
            )}
          </div>
        </div>

        {/* Main Conversation Container */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
          {/* Landing / Empty State */}
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-xl mx-auto py-12 space-y-5">
              <div className="p-4 bg-vbc-blue-light/50 border border-vbc-blue/20 rounded-2xl text-vbc-blue shadow-sm animate-pulse">
                <Sparkles size={36} />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-bold text-vbc-navy">ACO Intelligence Assistant</h3>
                <p className="text-xs text-vbc-gray leading-relaxed max-w-md">
                  Ask real-time questions about financial performance, risk anomalies, provider variation, forecasts, quality scores, or peer benchmark comparisons for <strong className="text-vbc-navy">{activeAcoName}</strong> (PY {selectedYear}).
                </p>
              </div>
            </div>
          )}

          {/* Conversation Messages */}
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start space-x-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.sender === 'assistant' && (
                <div className="p-2 bg-vbc-navy text-white rounded-lg shrink-0 mt-1 shadow-xs">
                  <Bot size={16} />
                </div>
              )}

              <div
                className={`rounded-2xl p-4 text-xs leading-relaxed max-w-[85%] sm:max-w-[75%] shadow-sm ${
                  msg.sender === 'user'
                    ? 'bg-vbc-navy text-white rounded-tr-xs'
                    : 'bg-white border border-vbc-gray-light text-vbc-navy rounded-tl-xs space-y-3'
                }`}
              >
                {/* Main text content */}
                <div className="whitespace-pre-line font-normal">{msg.text}</div>

                {/* Key Factors Bullets */}
                {msg.keyFactors && msg.keyFactors.length > 0 && (
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-1.5">
                    <span className="text-[10px] uppercase font-bold text-vbc-gray block tracking-wider">Key Observed Factors</span>
                    <ul className="space-y-1 text-[11px] text-vbc-navy">
                      {msg.keyFactors.map((f, idx) => (
                        <li key={idx} className="flex items-start space-x-1.5">
                          <span className="text-vbc-blue font-bold">•</span>
                          <span>{f}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommended Action */}
                {msg.recommendedAction && (
                  <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-emerald-950 space-y-1">
                    <span className="text-[10px] uppercase font-bold text-emerald-800 flex items-center space-x-1 tracking-wider">
                      <Lightbulb size={12} className="text-emerald-700" />
                      <span>Recommended Management Priority</span>
                    </span>
                    <p className="text-[11px] font-medium leading-relaxed">{msg.recommendedAction}</p>
                  </div>
                )}

                {/* Source Data Metadata Footer */}
                {msg.sourceData && (
                  <div className="pt-1 flex items-center justify-between text-[10px] text-vbc-gray border-t border-slate-100">
                    <span className="flex items-center space-x-1">
                      <ShieldCheck size={12} className="text-vbc-green-dark" />
                      <span>Grounded in authoritative data ({msg.acoId || activeAcoId} • PY {msg.year || selectedYear})</span>
                    </span>
                    <span className="italic">{msg.sourceData}</span>
                  </div>
                )}
              </div>

              {msg.sender === 'user' && (
                <div className="p-2 bg-vbc-blue text-white rounded-lg shrink-0 mt-1 shadow-xs">
                  <User size={16} />
                </div>
              )}
            </div>
          ))}

          {/* Loading Indicator */}
          {loading && (
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-vbc-navy text-white rounded-lg shrink-0">
                <Bot size={16} />
              </div>
              <div className="bg-white border border-vbc-gray-light rounded-2xl rounded-tl-xs px-4 py-3 text-xs text-vbc-gray flex items-center space-x-2 shadow-xs">
                <Loader2 size={14} className="animate-spin text-vbc-blue" />
                <span>Analyzing {activeAcoName} performance context...</span>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 bg-white border-t border-vbc-gray-light shrink-0">
          <div className="flex items-end space-x-2 bg-gray-50 border border-vbc-gray-light rounded-xl p-2 focus-within:border-vbc-blue focus-within:bg-white transition-colors">
            <textarea
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Ask a question about ${activeAcoName} (e.g., "Why is this ACO high risk?", "What is driving PMPM variance?", "What should we improve next year?")...`}
              className="flex-1 bg-transparent text-xs text-vbc-navy placeholder:text-vbc-gray focus:outline-none resize-none min-h-[38px] max-h-[120px] py-2 px-1"
              rows={1}
            />
            <button
              onClick={() => handleSend()}
              disabled={!inputQuery.trim() || loading}
              className="bg-vbc-blue hover:bg-vbc-blue-medium disabled:opacity-40 disabled:cursor-not-allowed text-white p-2.5 rounded-lg shadow-sm transition-colors shrink-0"
              title="Send message"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default AIAssistantPage;
