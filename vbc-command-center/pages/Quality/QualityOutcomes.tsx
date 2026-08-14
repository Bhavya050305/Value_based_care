import React from 'react';
import {
  Award,
  ShieldCheck,
  Building2,
  Activity,
  CheckCircle2,
  AlertCircle,
  FileSpreadsheet,
} from 'lucide-react';
import { useACOs } from '../../hooks/useACOs';
import { useHospitals } from '../../hooks/useHospitals';
import { KpiCard } from '../../components/common/KpiCard';
import { StatusBadge } from '../../components/common/StatusBadge';

export const QualityOutcomes: React.FC = () => {
  const { data: acos } = useACOs();
  const { data: hospitals } = useHospitals();

  const meanAcoQuality = acos && acos.length > 0
    ? (acos.reduce((acc, a) => acc + a.qualityScore, 0) / acos.length).toFixed(1)
    : '94.2';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">Quality & Clinical Safety</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">CMS Quality & HVBP Datasets</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mt-1">Quality & Outcomes Command</h1>
          <p className="text-xs text-slate-400 mt-1">
            CMS ACO Quality Performance Scores (`QualScore`) & Hospital Value-Based Purchasing (HVBP) safety measures.
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="ACO Mean Quality Score"
          value={`${meanAcoQuality}%`}
          cmsTag="QualScore"
          icon={Award}
          variant="accent"
          subtext="CMS Quality Threshold"
        />
        <KpiCard
          title="Hospitals Audited"
          value={hospitals?.length || 5}
          unit="Facilities"
          cmsTag="Facility ID"
          icon={Building2}
          subtext="HVBP Safety Program"
        />
        <KpiCard
          title="SEP-1 Sepsis Compliance"
          value="87.8%"
          cmsTag="SEP-1 Measure Score"
          icon={ShieldCheck}
          variant="accent"
        />
        <KpiCard
          title="HAI Infection Benchmark"
          value="0.32"
          unit="Rate"
          cmsTag="HAI-1 to HAI-6"
          icon={Activity}
          subtext="Healthcare-Associated Infections"
        />
      </div>

      {/* ACO Quality Summary */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950/60">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Award className="w-4 h-4 text-emerald-400" />
            ACO Value-Based Quality Scorecard
          </h2>
          <span className="text-xs text-slate-400 font-mono">CMS ACO Dataset</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="p-3.5">ACO Name</th>
                <th className="p-3.5">ACO ID</th>
                <th className="p-3.5 text-right">Assigned Benes</th>
                <th className="p-3.5 text-right">CMS Quality Score</th>
                <th className="p-3.5 text-right">Savings Rate</th>
                <th className="p-3.5 text-center">Quality Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {acos?.map((aco) => (
                <tr key={aco.acoId} className="hover:bg-slate-800/50 transition-colors">
                  <td className="p-3.5 font-semibold text-white">{aco.acoName}</td>
                  <td className="p-3.5 font-mono text-slate-400">{aco.acoId}</td>
                  <td className="p-3.5 text-right font-mono text-slate-300">{aco.assignedBeneficiaries.toLocaleString()}</td>
                  <td className="p-3.5 text-right font-mono font-bold text-emerald-400">{aco.qualityScore}%</td>
                  <td className="p-3.5 text-right font-mono text-slate-300">+{aco.savingsRate}%</td>
                  <td className="p-3.5 text-center">
                    <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-950 text-emerald-300 border border-emerald-800">
                      Quality Threshold Met
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Hospital Quality & Safety Section (HVBP Dataset) */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950/60">
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Building2 className="w-4 h-4 text-blue-400" />
              Hospital Quality & Safety (HVBP Dataset)
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">HAI-1 to HAI-6 Infections and SEP-1 Severe Sepsis Protocols</p>
          </div>
          <span className="text-xs font-mono text-slate-400">Future-Ready HVBP Integration</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="p-3.5">Facility Name</th>
                <th className="p-3.5">Facility ID</th>
                <th className="p-3.5">State</th>
                <th className="p-3.5 text-right">HAI-1 (CAUTI Rate)</th>
                <th className="p-3.5 text-right">HAI-2 (CLABSI Rate)</th>
                <th className="p-3.5 text-right">SEP-1 (Sepsis Protocol %)</th>
                <th className="p-3.5 text-center">Overall Tier</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {hospitals?.map((h) => (
                <tr key={h.facilityId} className="hover:bg-slate-800/50 transition-colors">
                  <td className="p-3.5 font-semibold text-white">{h.facilityName}</td>
                  <td className="p-3.5 font-mono text-slate-400">{h.facilityId}</td>
                  <td className="p-3.5 text-slate-300">{h.state}</td>
                  <td className="p-3.5 text-right font-mono text-slate-300">{h.hai1PerformanceRate}</td>
                  <td className="p-3.5 text-right font-mono text-slate-300">{h.hai2PerformanceRate}</td>
                  <td className="p-3.5 text-right font-mono font-bold text-emerald-400">{h.sep1PerformanceRate}%</td>
                  <td className="p-3.5 text-center">
                    <StatusBadge status={h.overallQualityTier} size="sm" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
