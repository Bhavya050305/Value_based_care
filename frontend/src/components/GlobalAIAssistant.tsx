import React, { useState, useEffect, useRef } from 'react';
import { useDataMode } from '../context/DataModeContext';
import { useAIContext } from '../context/AIContextContext';
import { aiService } from '../services/aiService';
import { MessageSquare, X, Send, Bot, User, Sparkles, AlertCircle } from 'lucide-react';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  keyPoints?: string[];
  source?: string;
  timestamp: Date;
}

// ONE global, contextual assistant — mounted once from Layout, present on
// every authenticated page. It is not an "AI Insights" dashboard; it answers
// using the structured context of whatever page/ACO/filters are currently active.
export const GlobalAIAssistant: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { dataMode } = useDataMode();
  const { aiContext } = useAIContext();

  const welcomeText = () =>
    `Hi, I'm the VBC CommandIQ AI Assistant. I'm currently grounded in ${aiService.describeContext(aiContext)}. Ask me about performance, drivers, forecast, peers, or what to review next.`;

  const [messages, setMessages] = useState<Message[]>([
    { id: 'welcome', sender: 'assistant', text: welcomeText(), timestamp: new Date() }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const lastPageRef = useRef<string>(aiContext.page);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // When the page/ACO context meaningfully changes, drop a small system note
  // into the conversation rather than wiping history, so the assistant stays
  // contextual without feeling amnesiac.
  useEffect(() => {
    if (lastPageRef.current !== aiContext.page) {
      lastPageRef.current = aiContext.page;
      setMessages((prev) => [
        ...prev,
        {
          id: `ctx-${Date.now()}`,
          sender: 'assistant',
          text: `Context updated — now looking at ${aiService.describeContext(aiContext)}.`,
          timestamp: new Date()
        }
      ]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [aiContext.page, aiContext.acoId]);

  const quickQuestions = [
    { label: 'Why is this at risk?', q: 'Why is this ACO at risk?' },
    { label: 'What are the main drivers?', q: 'What are the main performance drivers?' },
    { label: 'Which provider varies most?', q: 'Which providers have the highest variation?' },
    { label: 'What should I review next?', q: 'Which areas need review?' }
  ];

  const handleSend = async (question: string) => {
    if (!question.trim()) return;

    const userMsg: Message = { id: `user-${Date.now()}`, sender: 'user', text: question, timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsTyping(true);

    try {
      const response = await aiService.ask(question, aiContext, dataMode);
      setTimeout(() => {
        setIsTyping(false);
        if (response.success) {
          setMessages((prev) => [
            ...prev,
            {
              id: `ai-${Date.now()}`,
              sender: 'assistant',
              text: response.data.answer,
              keyPoints: response.data.keyPoints,
              source: response.source,
              timestamp: new Date()
            }
          ]);
        } else {
          setMessages((prev) => [
            ...prev,
            {
              id: `ai-err-${Date.now()}`,
              sender: 'assistant',
              text: 'In CONNECTED mode, the FastAPI/Ollama assistant endpoint must be configured first. Switch to DEMO mode to see full contextual responses.',
              timestamp: new Date()
            }
          ]);
        }
      }, 650);
    } catch {
      setIsTyping(false);
      setMessages((prev) => [
        ...prev,
        { id: `ai-err-${Date.now()}`, sender: 'assistant', text: 'An error occurred. Please try again.', timestamp: new Date() }
      ]);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {isOpen && (
        <div className="bg-white rounded-2xl border border-vbc-gray-light shadow-2xl w-[350px] sm:w-[400px] h-[540px] flex flex-col overflow-hidden mb-4 animate-scaleUp">
          <div className="bg-vbc-navy text-white p-4 flex items-center justify-between">
            <div className="flex items-center space-x-2 overflow-hidden">
              <div className="p-1.5 bg-vbc-blue rounded-lg text-white flex-shrink-0">
                <Sparkles size={16} className="text-white" />
              </div>
              <div className="overflow-hidden">
                <h3 className="font-bold text-xs">VBC AI Assistant</h3>
                <span className="text-[10px] text-vbc-gray-light/80 block truncate max-w-[240px]">
                  Context: {aiService.describeContext(aiContext)}
                </span>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} className="text-vbc-gray hover:text-white p-1 rounded transition-colors flex-shrink-0">
              <X size={18} />
            </button>
          </div>

          {dataMode === 'connected' && (
            <div className="bg-emerald-50 px-3 py-1.5 border-b border-emerald-100 flex items-center space-x-2 text-[10px] text-emerald-800">
              <AlertCircle size={12} className="flex-shrink-0 text-emerald-600 animate-pulse" />
              <span>Connected Mode active. FastAPI AI Assistant Engine connected.</span>
            </div>
          )}

          <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-gray-50/50">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex space-x-2.5 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.sender === 'assistant' && (
                  <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 border border-indigo-100 flex items-center justify-center flex-shrink-0">
                    <Bot size={16} />
                  </div>
                )}
                <div className="space-y-1 max-w-[75%]">
                  <div
                    className={`p-3 rounded-xl text-xs leading-relaxed ${
                      msg.sender === 'user'
                        ? 'bg-vbc-blue text-white rounded-tr-none'
                        : 'bg-white text-vbc-navy border border-vbc-gray-light rounded-tl-none shadow-sm'
                    }`}
                  >
                    {msg.text}
                    {msg.keyPoints && msg.keyPoints.length > 0 && (
                      <ul className="mt-2.5 space-y-1 pl-4 list-disc text-vbc-navy font-medium text-[11px]">
                        {msg.keyPoints.map((pt, idx) => (
                          <li key={idx}>{pt}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                  {msg.source && <span className="text-[9px] text-vbc-gray/70 block uppercase px-1">Source: {msg.source}</span>}
                </div>
                {msg.sender === 'user' && (
                  <div className="w-8 h-8 rounded-lg bg-vbc-blue text-white flex items-center justify-center flex-shrink-0">
                    <User size={16} />
                  </div>
                )}
              </div>
            ))}

            {isTyping && (
              <div className="flex space-x-2.5 justify-start">
                <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 border border-indigo-100 flex items-center justify-center flex-shrink-0 animate-pulse">
                  <Bot size={16} />
                </div>
                <div className="bg-white border border-vbc-gray-light rounded-xl rounded-tl-none p-3 shadow-sm flex items-center space-x-1">
                  <div className="w-1.5 h-1.5 bg-vbc-gray rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-1.5 h-1.5 bg-vbc-gray rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-1.5 h-1.5 bg-vbc-gray rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {messages.length <= 2 && !isTyping && (
            <div className="p-3 border-t border-vbc-gray-light bg-white space-y-2">
              <span className="text-[10px] font-bold text-vbc-gray uppercase tracking-wider block">Quick Questions</span>
              <div className="grid grid-cols-1 gap-1.5">
                {quickQuestions.map((pq, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(pq.q)}
                    className="text-left w-full text-xs text-vbc-blue hover:bg-vbc-blue-light/50 px-2.5 py-1.5 rounded-lg border border-vbc-blue/10 font-semibold transition-colors truncate"
                  >
                    {pq.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend(inputText);
            }}
            className="p-3 border-t border-vbc-gray-light bg-white flex items-center space-x-2"
          >
            <input
              type="text"
              placeholder="Ask a question..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="flex-1 bg-gray-50 border border-vbc-gray-light hover:border-vbc-gray focus:border-vbc-blue focus:outline-none px-3 py-2 rounded-lg text-xs"
            />
            <button
              type="submit"
              disabled={!inputText.trim() || isTyping}
              className="p-2 bg-vbc-blue text-white rounded-lg hover:bg-vbc-blue-medium disabled:opacity-40 transition-opacity"
            >
              <Send size={15} />
            </button>
          </form>
        </div>
      )}

      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-12 h-12 rounded-full bg-vbc-blue hover:bg-vbc-blue-medium hover:scale-105 transition-all text-white flex items-center justify-center shadow-xl border border-white/20 relative"
      >
        {isOpen ? <X size={20} /> : <MessageSquare size={20} />}
        {!isOpen && <span className="absolute -top-0.5 -right-0.5 w-3 h-3 bg-vbc-red rounded-full border border-white animate-ping"></span>}
      </button>
    </div>
  );
};
export default GlobalAIAssistant;
