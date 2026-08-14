import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { TooltipHelp } from './TooltipHelp';

interface KpiCardProps {
  title: string;
  value: string | number;
  unit?: string;
  cmsTag?: string;
  changePct?: number;
  changeLabel?: string;
  icon?: LucideIcon;
  tooltip?: string;
  subtext?: string;
  variant?: 'default' | 'accent' | 'warning' | 'alert';
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  unit = '',
  cmsTag,
  changePct,
  changeLabel = 'vs prev year',
  icon: Icon,
  tooltip,
  subtext,
  variant = 'default',
}) => {
  const isPositive = changePct !== undefined && changePct > 0;
  const isNegative = changePct !== undefined && changePct < 0;

  let borderColor = 'border-slate-800/80 hover:border-slate-700';
  let iconBg = 'bg-slate-800/80 text-blue-400';

  if (variant === 'accent') {
    borderColor = 'border-blue-800/40 bg-blue-950/10 hover:border-blue-700/60';
    iconBg = 'bg-blue-900/40 text-blue-400';
  } else if (variant === 'warning') {
    borderColor = 'border-amber-800/40 bg-amber-950/10';
    iconBg = 'bg-amber-900/40 text-amber-400';
  } else if (variant === 'alert') {
    borderColor = 'border-rose-800/40 bg-rose-950/10';
    iconBg = 'bg-rose-900/40 text-rose-400';
  }

  return (
    <div className={`bg-slate-900/70 backdrop-blur-sm border ${borderColor} rounded-xl p-4 transition-all duration-200 shadow-lg shadow-black/20 hover:shadow-xl`}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-1.5">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
          {tooltip && <TooltipHelp text={tooltip} />}
        </div>
        {Icon && (
          <div className={`p-2 rounded-lg ${iconBg}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="flex items-baseline gap-1 my-1">
        <span className="text-2xl font-bold tracking-tight text-white font-mono">{value}</span>
        {unit && <span className="text-xs font-medium text-slate-400">{unit}</span>}
      </div>

      <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-800/60">
        {changePct !== undefined ? (
          <div className="flex items-center text-xs font-medium">
            {isPositive ? (
              <span className="flex items-center text-emerald-400">
                <TrendingUp className="w-3.5 h-3.5 mr-0.5" />
                +{changePct}%
              </span>
            ) : isNegative ? (
              <span className="flex items-center text-rose-400">
                <TrendingDown className="w-3.5 h-3.5 mr-0.5" />
                {changePct}%
              </span>
            ) : (
              <span className="flex items-center text-slate-400">
                <Minus className="w-3.5 h-3.5 mr-0.5" />
                0.0%
              </span>
            )}
            <span className="text-slate-500 ml-1.5 text-[11px]">{changeLabel}</span>
          </div>
        ) : (
          <span className="text-[11px] text-slate-500">{subtext || 'Verified Metric'}</span>
        )}

        {cmsTag && (
          <span className="text-[10px] font-mono font-medium px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/60">
            {cmsTag}
          </span>
        )}
      </div>
    </div>
  );
};
