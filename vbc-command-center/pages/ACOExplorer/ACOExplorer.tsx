import React, { useState } from 'react';
import {
  Building2,
  DollarSign,
  Award,
  Users,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  X,
  ShieldCheck,
  FileSpreadsheet,
} from 'lucide-react';
import { useACOs } from '../../hooks/useACOs';
import { ACORecord } from '../../types/aco';
import { KpiCard } from '../../components/common/KpiCard';
import { StatusBadge } from '../../components/common/StatusBadge';
import { formatCurrency, formatNumber } from '../../utils/formatting';

export const ACOExplorer: React.FC = () => {
  const { data: acos, isLoading } = useACOs();
  const [selectedAco, setSelectedAco] = useState<ACORecord | null>(null);

  const totalAssignedBenes = (acos || []).reduce((sum, a) => sum + a.assignedBeneficiaries, 0);
  const totalGeneratedSavings = (acos || []).reduce((sum, a) => sum + a.generatedSavingsLoss, 0);
  const avgQualityScore = acos && acos.length > 0
    ? (acos.reduce((sum, a) => sum + a.qualityScore, 0) / acos.length).toFixed(1)
    : '0';

  const exportACOCSV = () => {
    if (!acos) return;
    const headers = ['ACO ID', 'ACO Name', 'Track', 'Risk Model', 'Assigned Benes', 'Quality Score', 'Savings Rate (%)', 'Generated Savings/Loss ($)'];
    const rows = acos.map((a) => [
      a.acoId,
      `"${a.acoName}"`,
      a.currentTrack,
      a.riskModel,
      a.assignedBeneficiaries,
      a.qualityScore,
      a.savingsRate,
      a.generatedSavingsLoss,
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'ACO_Performance_Summary_2024.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">Medicare Shared Savings Program</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">ACO Dataset</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mt-1">ACO Explorer</h1>
          <p className="text-xs text-slate-400 mt-1">
            Contract performance, quality benchmarks, and shared savings distribution across MSSP ACO entities.
          </p>
        </div>

        <button
          onClick={exportACOCSV}
          className="flex items-center gap-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg px-3 py-2 text-xs font-medium text-slate-200 transition-colors"
        >
          <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
          <span>Export ACO Report CSV</span>
        </button>
      </div>

      {/* KPI Header Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Active ACO Contracts"
          value={acos?.length || 0}
          unit="ACOs"
          cmsTag="ACO_ID"
          icon={Building2}
          subtext="Medicare Shared Savings"
        />
        <KpiCard
          title="Assigned Beneficiaries"
          value={formatNumber(totalAssignedBenes)}
          unit="Benes"
          cmsTag="N_AB"
          icon={Users}
          variant="accent"
        />
        <KpiCard
          title="Net Generated Savings"
          value={formatCurrency(totalGeneratedSavings)}
          cmsTag="GenSaveLoss"
          icon={DollarSign}
          variant={totalGeneratedSavings > 0 ? 'accent' : 'alert'}
          tooltip="Total generated savings or losses relative to updated benchmark."
        />
        <KpiCard
          title="Mean Quality Score"
          value={`${avgQualityScore}%`}
          cmsTag="QualScore"
          icon={Award}
          subtext="CMS Quality Benchmark"
          variant="accent"
        />
      </div>

      {/* ACO Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Building2 className="w-4 h-4 text-emerald-400" />
            ACO Contract Ranking & Performance Summary
          </h2>
          <span className="text-xs text-slate-400 font-mono">{acos?.length || 0} Records</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="p-3.5">ACO Name & ID</th>
                <th className="p-3.5">Track & Model</th>
                <th className="p-3.5 text-right">Beneficiaries</th>
                <th className="p-3.5 text-right">Quality Score</th>
                <th className="p-3.5 text-right">Savings Rate</th>
                <th className="p-3.5 text-right">Generated Savings/Loss</th>
                <th className="p-3.5 text-right">Per Capita Exp PY</th>
                <th className="p-3.5 text-center">Status</th>
                <th className="p-3.5 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {isLoading ? (
                <tr>
                  <td colSpan={9} className="p-8 text-center text-slate-500">Loading ACO records...</td>
                </tr>
              ) : (
                acos?.map((aco) => (
                  <tr key={aco.acoId} className="hover:bg-slate-800/50 transition-colors">
                    <td className="p-3.5 font-medium text-white">
                      <div className="font-semibold text-slate-200">{aco.acoName}</div>
                      <div className="text-[11px] font-mono text-slate-400">ID: {aco.acoId}</div>
                    </td>
                    <td className="p-3.5 text-slate-300">
                      <div className="font-medium">{aco.currentTrack}</div>
                      <div className="text-[11px] text-slate-500">{aco.riskModel}</div>
                    </td>
                    <td className="p-3.5 text-right font-mono text-slate-200">
                      {formatNumber(aco.assignedBeneficiaries)}
                    </td>
                    <td className="p-3.5 text-right font-mono text-emerald-400 font-semibold">
                      {aco.qualityScore}%
                    </td>
                    <td className="p-3.5 text-right font-mono font-medium text-slate-200">
                      {aco.savingsRate > 0 ? `+${aco.savingsRate}%` : `${aco.savingsRate}%`}
                    </td>
                    <td className={`p-3.5 text-right font-mono font-bold ${aco.generatedSavingsLoss >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {formatCurrency(aco.generatedSavingsLoss)}
                    </td>
                    <td className="p-3.5 text-right font-mono text-slate-300">
                      {formatCurrency(aco.perCapitaExpenditureTotalPY)}
                    </td>
                    <td className="p-3.5 text-center">
                      <StatusBadge status={aco.performanceStatus} size="sm" />
                    </td>
                    <td className="p-3.5 text-center">
                      <button
                        onClick={() => setSelectedAco(aco)}
                        className="px-2.5 py-1 text-[11px] font-medium bg-blue-600/20 hover:bg-blue-600 text-blue-300 hover:text-white rounded border border-blue-500/30 transition-colors"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ACO Detail Drilldown Modal */}
      {selectedAco && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-3xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start border-b border-slate-800 pb-3">
              <div>
                <span className="text-xs font-mono text-blue-400">ACO ID: {selectedAco.acoId}</span>
                <h2 className="text-xl font-bold text-white">{selectedAco.acoName}</h2>
                <span className="text-xs text-slate-400">{selectedAco.riskModel} • Track: {selectedAco.currentTrack}</span>
              </div>
              <button onClick={() => setSelectedAco(null)} className="p-1 text-slate-400 hover:text-white rounded bg-slate-800">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 bg-slate-950 rounded border border-slate-800">
                <span className="text-slate-500 block">Generated Savings</span>
                <span className="text-base font-bold font-mono text-emerald-400">{formatCurrency(selectedAco.generatedSavingsLoss)}</span>
              </div>
              <div className="p-3 bg-slate-950 rounded border border-slate-800">
                <span className="text-slate-500 block">Quality Score</span>
                <span className="text-base font-bold font-mono text-blue-400">{selectedAco.qualityScore}%</span>
              </div>
              <div className="p-3 bg-slate-950 rounded border border-slate-800">
                <span className="text-slate-500 block">Assigned Benes</span>
                <span className="text-base font-bold font-mono text-slate-200">{formatNumber(selectedAco.assignedBeneficiaries)}</span>
              </div>
              <div className="p-3 bg-slate-950 rounded border border-slate-800">
                <span className="text-slate-500 block">Per Capita Spend</span>
                <span className="text-base font-bold font-mono text-slate-200">{formatCurrency(selectedAco.perCapitaExpenditureTotalPY)}</span>
              </div>
            </div>

            <div className="border-t border-slate-800 pt-3">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Utilization & Quality Markers</h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                <div className="p-2 bg-slate-950 rounded">
                  <span className="text-slate-500">Inpatient Admits / 1K:</span>
                  <span className="font-mono font-bold text-slate-200 ml-1">{selectedAco.admissionsPer1000}</span>
                </div>
                <div className="p-2 bg-slate-950 rounded">
                  <span className="text-slate-500">ED Visits / 1K:</span>
                  <span className="font-mono font-bold text-slate-200 ml-1">{selectedAco.edVisitsPer1000}</span>
                </div>
                <div className="p-2 bg-slate-950 rounded">
                  <span className="text-slate-500">SNF Avg Stay (Days):</span>
                  <span className="font-mono font-bold text-slate-200 ml-1">{selectedAco.snfLengthOfStay}</span>
                </div>
              </div>
            </div>

            <div className="pt-2 text-right">
              <button
                onClick={() => setSelectedAco(null)}
                className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-medium"
              >
                Close Summary
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
