import React from 'react';
import { SHAPFeature } from '../types';
import { Info } from 'lucide-react';

interface SHAPChartProps {
  features: SHAPFeature[];
  predictedOutcome: 'LOSS' | 'GAIN';
  riskProbability: number;
}

export const SHAPChart: React.FC<SHAPChartProps> = ({
  features,
  predictedOutcome,
  riskProbability
}) => {
  // DEMO SHAP VALUES
  // FINAL INTEGRATION: Replace with /api/ml/aco-risk/{acoId}/shap

  // Find max impact value for scaling the horizontal bars
  const maxImpact = Math.max(...features.map(f => Math.abs(f.impactValue)), 0.1);

  return (
    <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-6 space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-vbc-gray-light pb-4">
        <div>
          <h3 className="text-lg font-bold text-vbc-navy">ML Risk Prediction & Explainability</h3>
          <p className="text-xs text-vbc-gray mt-0.5">
            SHAP (SHapley Additive exPlanations) values outline the contribution weights of each feature.
          </p>
        </div>
        <div className="mt-3 md:mt-0 flex items-center space-x-2 bg-indigo-50/50 border border-indigo-100 rounded-lg p-2.5">
          <Info size={16} className="text-indigo-600 flex-shrink-0" />
          <span className="text-xs text-indigo-950 font-medium leading-relaxed">
            Predicted Risk: <strong className="font-bold text-indigo-700">{predictedOutcome === 'LOSS' ? 'HIGH RISK' : 'LOW RISK'} ({riskProbability}%)</strong>
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* SHAP bar list */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex justify-between text-xs font-bold text-vbc-gray border-b border-vbc-gray-light pb-1">
            <span>Clinical Feature & Value</span>
            <span>SHAP Impact Contribution</span>
          </div>

          <div className="space-y-3.5">
            {features.map((feature, idx) => {
              const isPositive = feature.direction === 'positive';
              const percentWidth = Math.min(100, (Math.abs(feature.impactValue) / maxImpact) * 100);
              
              return (
                <div key={idx} className="group flex flex-col space-y-1">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-vbc-navy flex items-center space-x-1.5">
                      <span>{feature.name}</span>
                      <span className="text-[10px] bg-vbc-gray-light text-vbc-navy/60 px-1.5 py-0.5 rounded font-normal">
                        {feature.featureValue}
                      </span>
                    </span>
                    <span className={`font-bold ${isPositive ? 'text-vbc-red-dark' : 'text-vbc-green-dark'}`}>
                      {isPositive ? '+' : ''}{feature.impactValue.toFixed(2)}
                    </span>
                  </div>

                  <div className="relative w-full h-6 flex items-center bg-gray-50 rounded border border-gray-100 overflow-hidden">
                    {/* Mid line */}
                    <div className="absolute left-1/2 top-0 bottom-0 w-px bg-vbc-gray/20 z-10"></div>
                    
                    {isPositive ? (
                      <div className="absolute left-1/2 right-0 h-full flex items-center">
                        <div
                          className="h-4 bg-vbc-red/80 hover:bg-vbc-red rounded-r transition-all duration-500 flex items-center justify-end pr-1 text-[9px] text-white font-bold"
                          style={{ width: `${percentWidth / 2}%` }}
                        >
                          +
                        </div>
                      </div>
                    ) : (
                      <div className="absolute right-1/2 left-0 h-full flex items-center justify-end">
                        <div
                          className="h-4 bg-vbc-green/80 hover:bg-vbc-green rounded-l transition-all duration-500 flex items-center pl-1 text-[9px] text-white font-bold"
                          style={{ width: `${percentWidth / 2}%` }}
                        >
                          −
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Info panel & Legend */}
        <div className="bg-vbc-blue-light border border-vbc-blue/20 rounded-xl p-5 flex flex-col justify-between">
          <div className="space-y-4">
            <h4 className="font-bold text-vbc-navy text-sm flex items-center space-x-1.5">
              <span>Why is this ACO predicted to be at risk?</span>
            </h4>
            <p className="text-xs text-vbc-navy/80 leading-relaxed">
              The model evaluates historical contract claims to predict whether the selected ACO will conclude with a **Shared Savings GAIN** or a **Shared Deficit LOSS**. 
            </p>
            <p className="text-xs text-vbc-navy/80 leading-relaxed font-semibold italic">
              "SHAP values show how each feature contributed to this ACO's predicted outcome."
            </p>
          </div>

          <div className="mt-6 pt-4 border-t border-vbc-blue/15 space-y-3">
            <span className="text-[10px] font-bold uppercase tracking-wider text-vbc-navy/60">
              SHAP Impact Legend
            </span>
            <div className="space-y-2">
              <div className="flex items-start space-x-2">
                <div className="w-3.5 h-3.5 bg-vbc-red/80 rounded border border-vbc-red mt-0.5 flex items-center justify-center text-[9px] text-white font-bold">+</div>
                <div>
                  <span className="text-xs font-semibold text-vbc-navy block">Positive SHAP</span>
                  <span className="text-[10px] text-vbc-gray block">
                    Increases predicted risk. Contributes toward a contract **LOSS**.
                  </span>
                </div>
              </div>
              
              <div className="flex items-start space-x-2">
                <div className="w-3.5 h-3.5 bg-vbc-green/80 rounded border border-vbc-green mt-0.5 flex items-center justify-center text-[9px] text-white font-bold">−</div>
                <div>
                  <span className="text-xs font-semibold text-vbc-navy block">Negative SHAP</span>
                  <span className="text-[10px] text-vbc-gray block">
                    Reduces predicted risk. Contributes toward a contract **GAIN**.
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
export default SHAPChart;
