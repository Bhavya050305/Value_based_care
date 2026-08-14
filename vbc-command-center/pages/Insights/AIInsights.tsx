import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Building2,
  User,
  Activity,
} from 'lucide-react';
import { useInsights } from '../../hooks/useInsights';

export const AIInsights: React.FC = () => {
  const navigate = useNavigate();
  const { data: insights, isLoading } = useInsights();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">Automated Intelligence</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 font-mono">
              Demo AI Insight
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mt-1">AI Insights Center</h1>
          <p className="text-xs text-slate-400 mt-1">
            Automated anomaly detection, cost driver identification, and clinical risk alignment analysis across contracted entities.
          </p>
        </div>
      </div>

      {/* Insights Feed */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="p-8 text-center text-slate-500">Loading AI portfolio insights...</div>
        ) : (
          insights?.map((insight) => (
            <div
              key={insight.id}
              className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col md:flex-row md:items-start justify-between gap-4 hover:border-slate-700 transition-colors"
            >
              <div className="space-y-3 flex-1">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 bg-blue-950 text-blue-300 border border-blue-800 rounded text-xs font-semibold">
                    {insight.category}
                  </span>
                  <span className="text-xs font-mono text-emerald-400 font-bold bg-emerald-950/60 border border-emerald-800/80 px-2 py-0.5 rounded">
                    {insight.impactEstimate}
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono ml-auto">
                    Confidence: {(insight.confidenceScore * 100).toFixed(0)}%
                  </span>
                </div>

                <h2 className="text-base font-bold text-white">{insight.title}</h2>
                <p className="text-xs text-slate-300 leading-relaxed">{insight.summary}</p>

                <div className="pt-2 border-t border-slate-800/80">
                  <span className="text-xs font-semibold text-slate-400 block mb-1">Potential Underlying Drivers:</span>
                  <ul className="list-disc list-inside space-y-0.5 text-xs text-slate-400 font-sans">
                    {insight.potentialDrivers.map((driver, idx) => (
                      <li key={idx}>{driver}</li>
                    ))}
                  </ul>
                </div>

                <div className="p-3 bg-blue-950/40 border border-blue-900/60 rounded-lg text-xs text-blue-200">
                  <strong>Suggested Investigation:</strong> {insight.suggestedAction}
                </div>
              </div>

              <div className="shrink-0 pt-2">
                {insight.npi && (
                  <button
                    onClick={() => navigate(`/providers/${insight.npi}`)}
                    className="px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg transition-colors flex items-center gap-1.5 shadow-md"
                  >
                    Provider Detail <ArrowRight className="w-4 h-4" />
                  </button>
                )}
                {insight.acoId && (
                  <button
                    onClick={() => navigate('/acos')}
                    className="px-3 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg transition-colors flex items-center gap-1.5 shadow-md"
                  >
                    ACO Explorer <ArrowRight className="w-4 h-4" />
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
