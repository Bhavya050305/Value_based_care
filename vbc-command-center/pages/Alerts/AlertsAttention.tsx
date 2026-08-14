import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  ShieldAlert,
  ArrowRight,
  CheckCircle2,
  DollarSign,
  TrendingUp,
  Activity,
  Users,
} from 'lucide-react';
import { useAlerts } from '../../hooks/useAlerts';
import { StatusBadge } from '../../components/common/StatusBadge';

export const AlertsAttention: React.FC = () => {
  const navigate = useNavigate();
  const { data: alerts, isLoading } = useAlerts();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-rose-400">Risk & Anomaly Center</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 font-mono">
              5 Active Warnings
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mt-1">Alerts & Attention Dashboard</h1>
          <p className="text-xs text-slate-400 mt-1">
            Automated outlier detection flagging payment variances, utilization spikes, high risk scores, and quality deficits.
          </p>
        </div>
      </div>

      {/* Alert Feed */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="p-8 text-center text-slate-500">Loading active alerts...</div>
        ) : (
          alerts?.map((alert) => (
            <div
              key={alert.id}
              className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-slate-700 transition-colors"
            >
              <div className="space-y-2 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <StatusBadge status={alert.severity} size="sm" />
                  <span className="text-xs font-bold text-slate-300 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                    {alert.category}
                  </span>
                  <span className="text-[11px] font-mono text-slate-500">{alert.timestamp}</span>
                </div>

                <div className="text-base font-bold text-white">
                  {alert.providerName || alert.acoName}
                  {alert.npi && <span className="text-xs font-mono text-slate-400 font-normal ml-2">NPI: {alert.npi}</span>}
                  {alert.acoId && <span className="text-xs font-mono text-slate-400 font-normal ml-2">ACO ID: {alert.acoId}</span>}
                </div>

                <div className="text-xs text-slate-300 flex flex-wrap items-center gap-4 font-mono bg-slate-950 p-2.5 rounded-lg border border-slate-800/80">
                  <div>
                    <span className="text-slate-500">Metric: </span>
                    <span className="text-slate-200 font-semibold">{alert.metricName}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Current: </span>
                    <span className="text-rose-400 font-bold">{alert.currentValue}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Benchmark: </span>
                    <span className="text-slate-300">{alert.benchmarkValue}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Variance: </span>
                    <span className="text-rose-400 font-bold">{alert.variance}</span>
                  </div>
                </div>

                <div className="text-xs text-slate-300 bg-blue-950/30 border border-blue-900/40 p-2.5 rounded-lg text-blue-200">
                  <strong>Recommended Payer Action:</strong> {alert.recommendedAction}
                </div>
              </div>

              <div className="shrink-0 flex items-center">
                {alert.npi && (
                  <button
                    onClick={() => navigate(`/providers/${alert.npi}`)}
                    className="px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-md transition-colors flex items-center gap-1.5"
                  >
                    Investigate Provider <ArrowRight className="w-4 h-4" />
                  </button>
                )}
                {alert.acoId && (
                  <button
                    onClick={() => navigate('/acos')}
                    className="px-3 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg shadow-md transition-colors flex items-center gap-1.5"
                  >
                    Investigate ACO <ArrowRight className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
