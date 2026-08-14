import React, { useState } from 'react';
import { HelpCircle } from 'lucide-react';

interface TooltipHelpProps {
  text: string;
  className?: string;
}

export const TooltipHelp: React.FC<TooltipHelpProps> = ({ text, className = '' }) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div
      className={`relative inline-flex items-center text-slate-400 hover:text-slate-200 cursor-help ${className}`}
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
      onClick={() => setIsVisible(!isVisible)}
    >
      <HelpCircle className="w-3.5 h-3.5 ml-1 transition-colors" />
      {isVisible && (
        <div className="absolute z-50 bottom-full mb-2 left-1/2 -translate-x-1/2 w-64 p-2.5 text-xs bg-slate-900 text-slate-200 rounded-lg border border-slate-700 shadow-xl leading-relaxed pointer-events-none transition-all animate-in fade-in zoom-in-95">
          {text}
          <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-slate-900" />
        </div>
      )}
    </div>
  );
};
