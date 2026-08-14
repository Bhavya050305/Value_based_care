import React from 'react';
import { env } from '../../config/env';
import { Database, ShieldCheck } from 'lucide-react';

export const DataSourceBadge: React.FC = () => {
  const isMock = env.isMock;

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium border font-mono transition-colors ${
        isMock
          ? 'bg-amber-950/70 text-amber-300 border-amber-800/80'
          : 'bg-emerald-950/70 text-emerald-300 border-emerald-800/80'
      }`}
      title={
        isMock
          ? 'Currently running on Synthetic CMS Demo Mock API (Phase 1). Backend integration will auto-switch to Live Data.'
          : 'Connected to Live CMS Datasets Backend API (Phase 2).'
      }
    >
      <span className={`w-2 h-2 rounded-full animate-pulse ${isMock ? 'bg-amber-400' : 'bg-emerald-400'}`} />
      <span className="uppercase tracking-wider">{isMock ? 'DEMO DATA' : 'LIVE DATA'}</span>
      {isMock ? <Database className="w-3 h-3 ml-0.5 text-amber-400" /> : <ShieldCheck className="w-3 h-3 ml-0.5 text-emerald-400" />}
    </div>
  );
};
