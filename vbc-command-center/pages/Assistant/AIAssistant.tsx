import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bot,
  Send,
  User,
  Sparkles,
  ArrowRight,
  HelpCircle,
  RotateCcw,
} from 'lucide-react';
import { queryAssistant, ChatMessage } from '../../services/assistant/assistantEngine';

export const AIAssistant: React.FC = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'msg-init',
      sender: 'assistant',
      text: `Hello! I am your **Value-Based Care Performance Assistant**.

I can answer questions regarding provider performance, CMS ACO benchmarks, utilization anomalies, chronic condition burdens, and contract savings opportunities.

Select a quick question below or ask anything about your portfolio dataset!`,
      timestamp: 'Just now',
      suggestedActions: [
        'Why is Provider Metropolitan Cardiology performing poorly?',
        'Which providers have unusually high utilization?',
        'What are the main portfolio cost drivers?',
        'Show providers with high Medicare payments',
      ],
    },
  ]);
  const [inputQuery, setInputQuery] = useState('');

  const handleSend = (queryText?: string) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim()) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    const botResponse = queryAssistant(textToSend);

    setMessages((prev) => [...prev, userMsg, botResponse]);
    setInputQuery('');
  };

  return (
    <div className="space-y-6 flex flex-col h-[calc(100vh-7rem)]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3 shrink-0">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-purple-400">Conversational Analytics</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 font-mono">
              Demo AI Assistant
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mt-1">AI Performance Assistant</h1>
          <p className="text-xs text-slate-400 mt-1">
            Query value-based contract datasets, explain provider variance, and identify intervention strategies.
          </p>
        </div>

        <button
          onClick={() =>
            setMessages([
              {
                id: 'msg-init',
                sender: 'assistant',
                text: 'Chat history reset. How can I assist with your payer analytics dataset?',
                timestamp: 'Just now',
              },
            ])
          }
          className="px-3 py-1.5 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-xs font-medium text-slate-300 rounded-lg flex items-center gap-1.5 transition-colors self-start sm:self-auto"
        >
          <RotateCcw className="w-3.5 h-3.5" /> Clear Chat
        </button>
      </div>

      {/* Chat Container */}
      <div className="flex-1 bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-2xl flex flex-col">
        {/* Messages List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-3xl ${msg.sender === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
            >
              <div
                className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 text-white shadow-md ${
                  msg.sender === 'user' ? 'bg-blue-600' : 'bg-purple-600'
                }`}
              >
                {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div
                className={`p-4 rounded-2xl text-xs space-y-2 leading-relaxed shadow-lg ${
                  msg.sender === 'user'
                    ? 'bg-blue-600 text-white rounded-tr-none'
                    : 'bg-slate-950 text-slate-200 border border-slate-800 rounded-tl-none'
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.text}</div>

                {/* Suggested Action Chips */}
                {msg.suggestedActions && msg.suggestedActions.length > 0 && (
                  <div className="pt-2 border-t border-slate-800/80 flex flex-wrap gap-1.5">
                    {msg.suggestedActions.map((prompt, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSend(prompt)}
                        className="px-2.5 py-1 bg-slate-900 hover:bg-purple-900/40 text-purple-300 border border-purple-800/60 rounded-full text-[11px] font-medium transition-colors text-left"
                      >
                        {prompt}
                      </button>
                    ))}
                  </div>
                )}

                {msg.dataRef?.npi && (
                  <div className="pt-2">
                    <button
                      onClick={() => navigate(`/providers/${msg.dataRef?.npi}`)}
                      className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-semibold flex items-center gap-1 transition-colors"
                    >
                      Open Provider NPI {msg.dataRef.npi} Detail <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}

                <div className="text-[10px] text-slate-500 font-mono text-right">{msg.timestamp}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Input Bar */}
        <div className="p-3 bg-slate-950 border-t border-slate-800 flex items-center gap-2">
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask AI Assistant about provider costs, ACO savings, utilization, or risk score drivers..."
            className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 font-sans"
          />
          <button
            onClick={() => handleSend()}
            disabled={!inputQuery.trim()}
            className="px-4 py-2.5 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-xs font-semibold rounded-xl shadow-lg transition-colors flex items-center gap-1.5"
          >
            <span>Send</span> <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
