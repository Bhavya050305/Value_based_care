import React, { useState } from 'react';
import {
  Sliders,
  DollarSign,
  TrendingDown,
  RotateCcw,
  Sparkles,
  Info,
  ShieldCheck,
} from 'lucide-react';
import { formatCurrency, formatPercent } from '../../utils/formatting';

export const WhatIfSimulator: React.FC = () => {
  // Input Sliders State
  const [reduceServicesPct, setReduceServicesPct] = useState<number>(-5);
  const [reducePaymentPct, setReducePaymentPct] = useState<number>(-3);
  const [improveUtilizationPct, setImproveUtilizationPct] = useState<number>(-4);
  const [increasePreventivePct, setIncreasePreventivePct] = useState<number>(10);

  // Baseline Portfolio Metrics (PY 2024)
  const baselinePayment = 34460000;
  const baselineServicesPerBene = 5.6;
  const baselineRiskScore = 1.34;

  // Real-time Calculations
  const combinedCostMultiplier = 1 + (reducePaymentPct + reduceServicesPct * 0.7 + improveUtilizationPct * 0.5) / 100;
  const projectedPayment = Math.round(baselinePayment * combinedCostMultiplier);
  const projectedSavings = baselinePayment - projectedPayment;

  const projectedUtilizationPct = Number((reduceServicesPct + improveUtilizationPct).toFixed(1));
  const projectedRiskChangePct = Number((-0.15 * increasePreventivePct).toFixed(1));
  const projectedRiskScore = (baselineRiskScore * (1 + projectedRiskChangePct / 100)).toFixed(2);

  const resetSimulator = () => {
    setReduceServicesPct(0);
    setReducePaymentPct(0);
    setImproveUtilizationPct(0);
    setIncreasePreventivePct(0);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">Interactive Modeling</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 font-mono">
              Scenario Engine
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mt-1">What-If Scenario Simulator</h1>
          <p className="text-xs text-slate-400 mt-1">
            Simulate financial savings, utilization reductions, and risk score adjustments by tweaking contract intervention levers.
          </p>
        </div>

        <div className="bg-amber-950/80 border border-amber-800/80 px-3 py-1.5 rounded-lg text-amber-300 text-xs font-mono flex items-center gap-2">
          <Info className="w-4 h-4 text-amber-400 shrink-0" />
          <span>Scenario-based estimate — not a financial forecast.</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Slider Controls Panel (2 Cols) */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg space-y-6">
          <div className="flex justify-between items-center pb-3 border-b border-slate-800">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Sliders className="w-4 h-4 text-blue-400" />
              Contract Intervention Levers
            </h2>
            <button
              onClick={resetSimulator}
              className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded border border-slate-700 flex items-center gap-1 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" /> Reset Levers
            </button>
          </div>

          {/* Slider 1: Services per Beneficiary */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="font-semibold text-slate-200">Reduce Services per Beneficiary</span>
              <span className="font-mono font-bold text-blue-400">{reduceServicesPct}%</span>
            </div>
            <input
              type="range"
              min="-15"
              max="15"
              value={reduceServicesPct}
              onChange={(e) => setReduceServicesPct(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>-15% (Aggressive Utilization Reduction)</span>
              <span>0%</span>
              <span>+15% (Volume Spikes)</span>
            </div>
          </div>

          {/* Slider 2: Medicare Payment Rate */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="font-semibold text-slate-200">Reduce Medicare Reimbursement Payment</span>
              <span className="font-mono font-bold text-emerald-400">{reducePaymentPct}%</span>
            </div>
            <input
              type="range"
              min="-15"
              max="15"
              value={reducePaymentPct}
              onChange={(e) => setReducePaymentPct(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>-15% (Fee Schedule Cut)</span>
              <span>0%</span>
              <span>+15% (Rate Increase)</span>
            </div>
          </div>

          {/* Slider 3: Improve Utilization Efficiency */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="font-semibold text-slate-200">Improve Utilization Care Management</span>
              <span className="font-mono font-bold text-purple-400">{improveUtilizationPct}%</span>
            </div>
            <input
              type="range"
              min="-15"
              max="15"
              value={improveUtilizationPct}
              onChange={(e) => setImproveUtilizationPct(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>-15% (Care Coordination Success)</span>
              <span>0%</span>
              <span>+15%</span>
            </div>
          </div>

          {/* Slider 4: Increase Preventive Care */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="font-semibold text-slate-200">Increase Preventive Care & AWV Reach</span>
              <span className="font-mono font-bold text-amber-400">+{increasePreventivePct}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="30"
              value={increasePreventivePct}
              onChange={(e) => setIncreasePreventivePct(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>0% Baseline</span>
              <span>+15%</span>
              <span>+30% Full AWV Coverage</span>
            </div>
          </div>
        </div>

        {/* Real-time Output Cards (1 Col) */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4 flex flex-col justify-between">
          <div className="pb-3 border-b border-slate-800">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-400" />
              Projected Scenario Outputs
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">Real-time simulation results</p>
          </div>

          <div className="space-y-3">
            {/* Projected Payment */}
            <div className="p-3.5 bg-slate-950 border border-slate-800 rounded-xl space-y-1">
              <span className="text-xs text-slate-400 block font-medium">Projected Medicare Payment</span>
              <span className="text-2xl font-bold font-mono text-white">{formatCurrency(projectedPayment)}</span>
              <div className="text-[11px] text-slate-500">Baseline: {formatCurrency(baselinePayment)}</div>
            </div>

            {/* Projected Savings */}
            <div className="p-3.5 bg-emerald-950/40 border border-emerald-800/80 rounded-xl space-y-1">
              <span className="text-xs text-emerald-400 block font-medium">Projected Net Savings</span>
              <span className={`text-2xl font-bold font-mono ${projectedSavings >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {projectedSavings >= 0 ? `+${formatCurrency(projectedSavings)}` : formatCurrency(projectedSavings)}
              </span>
              <div className="text-[11px] text-emerald-300/80">Estimated annual payer value impact</div>
            </div>

            {/* Projected Utilization */}
            <div className="p-3.5 bg-slate-950 border border-slate-800 rounded-xl flex justify-between items-center text-xs">
              <div>
                <span className="text-slate-400 block">Projected Utilization Change</span>
                <span className="text-slate-500 font-mono">Services / Bene impact</span>
              </div>
              <span className={`text-base font-bold font-mono ${projectedUtilizationPct <= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {projectedUtilizationPct > 0 ? `+${projectedUtilizationPct}%` : `${projectedUtilizationPct}%`}
              </span>
            </div>

            {/* Projected Risk Score */}
            <div className="p-3.5 bg-slate-950 border border-slate-800 rounded-xl flex justify-between items-center text-xs">
              <div>
                <span className="text-slate-400 block">Projected HCC Risk Score</span>
                <span className="text-slate-500 font-mono">Baseline: {baselineRiskScore}</span>
              </div>
              <span className="text-base font-bold font-mono text-purple-400">{projectedRiskScore} HCC</span>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-800 text-[11px] text-slate-500 leading-tight">
            Simulation applies deterministic business logic (`calculations.ts`) during Phase 1.
          </div>
        </div>
      </div>
    </div>
  );
};
