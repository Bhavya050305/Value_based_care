import React, { useState } from 'react';
import { MLPrediction } from '../types';
import StatusBadge from './StatusBadge';
import { Brain, Sparkles, TrendingDown, TrendingUp } from 'lucide-react';

interface RiskPredictionCardProps {
  prediction: MLPrediction;
  acoName: string;
  onExploreML?: () => void;
}

export const RiskPredictionCard: React.FC<RiskPredictionCardProps> = ({
  prediction,
  acoName,
  onExploreML
}) => {
  const [viewMode, setViewMode] = useState<'risk' | 'outcome'>('risk');

  const { riskCategory, riskProbability, predictedOutcome, expectedValue, confidence } = prediction;

  const isLoss = predictedOutcome === 'LOSS';
  const formattedValue = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 1
  }).format(Math.abs(expectedValue));

  return (
    <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-6 flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between border-b border-vbc-gray-light pb-4 mb-4">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
              <Brain size={20} />
            </div>
            <div>
              <h3 className="font-bold text-vbc-navy text-sm">ML Performance Outcome</h3>
              <p className="text-xs text-vbc-gray">{acoName}</p>
            </div>
          </div>
          <div className="inline-flex rounded-lg border border-vbc-gray-light p-0.5 bg-vbc-gray-light">
            <button
              onClick={() => setViewMode('risk')}
              className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${
                viewMode === 'risk'
                  ? 'bg-white text-vbc-navy shadow-sm'
                  : 'text-vbc-gray hover:text-vbc-navy'
              }`}
            >
              Risk
            </button>
            <button
              onClick={() => setViewMode('outcome')}
              className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${
                viewMode === 'outcome'
                  ? 'bg-white text-vbc-navy shadow-sm'
                  : 'text-vbc-gray hover:text-vbc-navy'
              }`}
            >
              Outcome
            </button>
          </div>
        </div>

        {viewMode === 'risk' ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-vbc-navy">Risk Assessment</span>
              <StatusBadge type="risk" value={riskCategory} />
            </div>
            
            <div>
              <div className="flex justify-between text-xs text-vbc-gray mb-1">
                <span>Loss Probability</span>
                <span className="font-semibold text-vbc-navy">{riskProbability}%</span>
              </div>
              <div className="w-full bg-vbc-gray-light rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${
                    riskCategory === 'HIGH'
                      ? 'bg-vbc-red'
                      : riskCategory === 'MEDIUM'
                        ? 'bg-vbc-orange'
                        : 'bg-vbc-green'
                  }`}
                  style={{ width: `${riskProbability}%` }}
                ></div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-vbc-navy">Predicted Outcome</span>
              <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${
                isLoss 
                  ? 'bg-vbc-red-light text-vbc-red-dark border-vbc-red/25' 
                  : 'bg-vbc-green-light text-vbc-green-dark border-vbc-green/25'
              }`}>
                {isLoss ? <TrendingDown size={14} className="mr-1" /> : <TrendingUp size={14} className="mr-1" />}
                {isLoss ? 'Expected Loss' : 'Expected Gain'}
              </span>
            </div>

            <div className="text-center py-2">
              <div className={`text-3xl font-extrabold ${isLoss ? 'text-vbc-red-dark' : 'text-vbc-green-dark'}`}>
                {isLoss ? '-' : '+'}{formattedValue}
              </div>
              <p className="text-xs text-vbc-gray mt-1">Projected Shared Savings Balance</p>
            </div>
          </div>
        )}

        <div className="mt-4 pt-4 border-t border-vbc-gray-light flex items-center justify-between text-xs text-vbc-gray">
          <div className="flex items-center space-x-1">
            <Sparkles size={12} className="text-amber-500" />
            <span>Prediction Confidence</span>
          </div>
          <span className="font-semibold text-vbc-navy">{confidence}%</span>
        </div>
      </div>

      {onExploreML && (
        <button
          onClick={onExploreML}
          className="w-full mt-4 bg-vbc-navy text-white text-xs font-semibold py-2 px-4 rounded-lg hover:bg-vbc-navy-light transition-colors flex items-center justify-center space-x-1"
        >
          <span>View ML Explainability</span>
          <Brain size={14} />
        </button>
      )}
    </div>
  );
};
export default RiskPredictionCard;
