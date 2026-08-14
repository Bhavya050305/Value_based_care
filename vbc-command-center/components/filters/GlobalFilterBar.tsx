import React from 'react';
import { Filter, RotateCcw, Calendar, MapPin, Stethoscope, AlertCircle, ShieldAlert } from 'lucide-react';
import { useFilterStore } from '../../store/filterStore';

export const GlobalFilterBar: React.FC = () => {
  const {
    year,
    state,
    providerType,
    riskLevel,
    performanceTier,
    beneficiaryVolume,
    setYear,
    setState,
    setProviderType,
    setRiskLevel,
    setPerformanceTier,
    setBeneficiaryVolume,
    resetFilters,
  } = useFilterStore();

  const isFiltered =
    state !== 'ALL' ||
    providerType !== 'ALL' ||
    riskLevel !== 'ALL' ||
    performanceTier !== 'ALL' ||
    beneficiaryVolume !== 'ALL';

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-lg space-y-3 font-sans">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-2">
        <div className="flex items-center gap-2 text-xs font-bold text-slate-300 uppercase tracking-wider">
          <Filter className="w-4 h-4 text-blue-400" />
          <span>Global Performance Filters</span>
        </div>

        {isFiltered && (
          <button
            onClick={resetFilters}
            className="flex items-center gap-1 text-xs text-rose-400 hover:text-rose-300 font-medium transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Reset All Filters
          </button>
        )}
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 text-xs">
        {/* Year */}
        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Performance Year</label>
          <select
            value={year}
            onChange={(e) => setYear(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500 font-medium"
          >
            <option value="2024">2024 PY</option>
            <option value="2023">2023 PY</option>
            <option value="2022">2022 PY</option>
          </select>
        </div>

        {/* State */}
        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">State / Geography</label>
          <select
            value={state}
            onChange={(e) => setState(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500 font-medium"
          >
            <option value="ALL">All States (National)</option>
            <option value="IL">Illinois (IL)</option>
            <option value="OH">Ohio (OH)</option>
            <option value="MI">Michigan (MI)</option>
            <option value="IN">Indiana (IN)</option>
            <option value="WI">Wisconsin (WI)</option>
          </select>
        </div>

        {/* Provider Specialty */}
        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Provider Specialty</label>
          <select
            value={providerType}
            onChange={(e) => setProviderType(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500 font-medium"
          >
            <option value="ALL">All Specialties</option>
            <option value="Cardiology">Cardiology</option>
            <option value="Internal Medicine">Internal Medicine</option>
            <option value="Family Practice">Family Practice</option>
            <option value="Orthopedic Surgery">Orthopedic Surgery</option>
            <option value="Nephrology">Nephrology</option>
          </select>
        </div>

        {/* Risk Level */}
        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Beneficiary Risk Level</label>
          <select
            value={riskLevel}
            onChange={(e) => setRiskLevel(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500 font-medium"
          >
            <option value="ALL">All Risk Tiers</option>
            <option value="High Risk (> 1.4 HCC)">High Risk (&gt; 1.4 HCC)</option>
            <option value="Moderate (1.0 - 1.4 HCC)">Moderate (1.0 - 1.4 HCC)</option>
            <option value="Low Risk (< 1.0 HCC)">Low Risk (&lt; 1.0 HCC)</option>
          </select>
        </div>

        {/* Performance Tier */}
        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Performance Tier</label>
          <select
            value={performanceTier}
            onChange={(e) => setPerformanceTier(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500 font-medium"
          >
            <option value="ALL">All Tiers</option>
            <option value="High Performance">High Performance</option>
            <option value="Moderate">Moderate</option>
            <option value="Needs Attention">Needs Attention</option>
          </select>
        </div>

        {/* Bene Volume */}
        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Beneficiary Volume</label>
          <select
            value={beneficiaryVolume}
            onChange={(e) => setBeneficiaryVolume(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500 font-medium"
          >
            <option value="ALL">All Volumes</option>
            <option value="High (> 1000 Benes)">High (&gt; 1,000 Benes)</option>
            <option value="Medium (500 - 1000 Benes)">Medium (500 - 1,000 Benes)</option>
            <option value="Low (< 500 Benes)">Low (&lt; 500 Benes)</option>
          </select>
        </div>
      </div>
    </div>
  );
};
