import React from 'react';
import { CheckCircle2, AlertTriangle, AlertCircle, Info } from 'lucide-react';

interface StatusBadgeProps {
  status: 'High Performance' | 'Moderate' | 'Needs Attention' | 'Shared Savings' | 'Shared Losses' | 'Break-even' | 'Critical' | 'High' | 'Medium' | 'Low' | string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  let style = 'bg-slate-800 text-slate-300 border-slate-700';
  let Icon = Info;

  if (['High Performance', 'Shared Savings', 'Low', 'Top Decile'].includes(status)) {
    style = 'bg-emerald-950/80 text-emerald-300 border-emerald-800/60';
    Icon = CheckCircle2;
  } else if (['Moderate', 'Break-even', 'Medium', 'Above Average', 'Average'].includes(status)) {
    style = 'bg-amber-950/80 text-amber-300 border-amber-800/60';
    Icon = AlertTriangle;
  } else if (['Needs Attention', 'Shared Losses', 'High', 'Critical', 'Needs Improvement'].includes(status)) {
    style = 'bg-rose-950/80 text-rose-300 border-rose-800/60';
    Icon = AlertCircle;
  }

  const px = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span className={`inline-flex items-center gap-1 font-medium rounded-full border ${style} ${px}`}>
      <Icon className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
      {status}
    </span>
  );
};
