import React from 'react';

interface KPICardProps {
  title: string;
  value: string | number;
  change?: string | number;
  changeType?: 'positive' | 'negative' | 'neutral';
  subtext?: string;
  icon?: React.ReactNode;
  loading?: boolean;
  /** Visually indicates this card's filter is currently active (e.g. a clicked risk KPI). */
  highlight?: boolean;
  /** Optional accent color used for the icon chip and highlight ring. */
  accent?: 'blue' | 'green' | 'orange' | 'red';
}

const accentClasses: Record<string, { chip: string; ring: string }> = {
  blue: { chip: 'bg-vbc-blue-light text-vbc-blue', ring: 'ring-2 ring-vbc-blue border-vbc-blue' },
  green: { chip: 'bg-vbc-green-light text-vbc-green-dark', ring: 'ring-2 ring-vbc-green border-vbc-green' },
  orange: { chip: 'bg-vbc-orange-light text-vbc-orange-dark', ring: 'ring-2 ring-vbc-orange border-vbc-orange' },
  red: { chip: 'bg-vbc-red-light text-vbc-red-dark', ring: 'ring-2 ring-vbc-red border-vbc-red' }
};

export const KPIcard: React.FC<KPICardProps> = ({
  title,
  value,
  change,
  changeType = 'neutral',
  subtext,
  icon,
  loading = false,
  highlight = false,
  accent = 'blue'
}) => {
  if (loading) {
    return (
      <div className="bg-white p-5 rounded-xl border border-vbc-gray-light shadow-card animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/2 mb-3"></div>
        <div className="h-8 bg-gray-200 rounded w-3/4 mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-2/3"></div>
      </div>
    );
  }

  const accentCls = accentClasses[accent] || accentClasses.blue;

  return (
    <div
      className={`bg-white p-5 rounded-xl border shadow-card hover:shadow-md transition-shadow flex items-start justify-between ${
        highlight ? accentCls.ring : 'border-vbc-gray-light'
      }`}
    >
      <div className="space-y-1">
        <span className="text-xs font-semibold uppercase tracking-wider text-vbc-gray">
          {title}
        </span>
        <div className="text-2xl font-bold text-vbc-navy">
          {value}
        </div>
        
        {(change || subtext) && (
          <div className="flex items-center space-x-1.5 text-xs">
            {change && (
              <span className={`font-semibold ${
                changeType === 'positive' 
                  ? 'text-vbc-green-dark' 
                  : changeType === 'negative' 
                    ? 'text-vbc-red-dark' 
                    : 'text-vbc-gray'
              }`}>
                {change}
              </span>
            )}
            {subtext && <span className="text-vbc-gray">{subtext}</span>}
          </div>
        )}
      </div>

      {icon && (
        <div className={`p-2.5 rounded-lg ${accentCls.chip}`}>
          {icon}
        </div>
      )}
    </div>
  );
};
export default KPIcard;
