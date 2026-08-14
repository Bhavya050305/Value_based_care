import React, { useState, useEffect } from 'react';
import {
  CheckSquare,
  TrendingUp,
  DollarSign,
  Award,
  Layers,
  ArrowRight,
  CheckCircle2,
} from 'lucide-react';
import { getRecommendations } from '../../services/recommendations/recommendationEngine';
import { RecommendationItem } from '../../types/recommendations';

export const Recommendations: React.FC = () => {
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRecommendations().then((res) => {
      setRecommendations(res);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">Actionable Payer Strategies</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono">
              recommendationService.ts
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mt-1">Recommended Actions</h1>
          <p className="text-xs text-slate-400 mt-1">
            Prioritized clinical, network, and financial interventions generated for care management and provider network teams.
          </p>
        </div>
      </div>

      {/* Recommendations Feed */}
      <div className="space-y-4">
        {loading ? (
          <div className="p-8 text-center text-slate-500">Loading recommendations from recommendationService...</div>
        ) : (
          recommendations.map((rec) => (
            <div
              key={rec.id}
              className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg space-y-3 hover:border-slate-700 transition-colors"
            >
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-white uppercase tracking-wider bg-slate-800 px-2.5 py-1 rounded">
                    {rec.category}
                  </span>
                  <span
                    className={`text-xs font-semibold px-2.5 py-0.5 rounded border ${
                      rec.impactLevel === 'High'
                        ? 'bg-rose-950 text-rose-300 border-rose-800'
                        : 'bg-amber-950 text-amber-300 border-amber-800'
                    }`}
                  >
                    Impact: {rec.impactLevel}
                  </span>
                </div>

                <div className="flex items-center gap-3 text-xs font-mono">
                  <span className="text-emerald-400 font-bold bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800">
                    Est. Savings: {rec.estimatedSavings}
                  </span>
                  <span className="text-slate-400">Status: <strong className="text-white">{rec.status}</strong></span>
                </div>
              </div>

              <div>
                <h2 className="text-base font-bold text-white">{rec.title}</h2>
                <p className="text-xs text-slate-300 mt-1 leading-relaxed">{rec.description}</p>
                {rec.targetProviderOrAco && (
                  <div className="text-xs text-slate-400 mt-1 font-mono">
                    Target Entities: <strong className="text-slate-200">{rec.targetProviderOrAco}</strong>
                  </div>
                )}
              </div>

              <div className="pt-2 border-t border-slate-800/80">
                <span className="text-xs font-semibold text-slate-400 block mb-1.5">Actionable Implementation Steps:</span>
                <div className="space-y-1 text-xs text-slate-300">
                  {rec.actionableSteps.map((step, idx) => (
                    <div key={idx} className="flex items-start gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                      <span>{step}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
