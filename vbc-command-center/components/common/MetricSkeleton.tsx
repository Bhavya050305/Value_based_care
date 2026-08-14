import React from 'react';

export const MetricSkeleton: React.FC = () => {
  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 animate-pulse">
      <div className="flex justify-between items-center mb-3">
        <div className="h-3 bg-slate-800 rounded w-24"></div>
        <div className="h-4 w-4 bg-slate-800 rounded-full"></div>
      </div>
      <div className="h-7 bg-slate-800 rounded w-32 mb-2"></div>
      <div className="h-3 bg-slate-800/60 rounded w-20"></div>
    </div>
  );
};
