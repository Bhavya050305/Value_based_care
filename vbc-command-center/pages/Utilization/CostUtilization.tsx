import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  TrendingUp,
  Activity,
  Users,
  FileSpreadsheet,
  AlertTriangle,
  ArrowRight,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from 'recharts';
import { useProviders, usePortfolioSummary } from '../../hooks/useProviders';
import { KpiCard } from '../../components/common/KpiCard';
import { GlobalFilterBar } from '../../components/filters/GlobalFilterBar';
import { formatNumber, formatCurrency } from '../../utils/formatting';

export const CostUtilization: React.FC = () => {
  const navigate = useNavigate();
  const { providers } = useProviders();
  const { data: summary } = usePortfolioSummary();

  const totalServices = summary?.totalServices || 0;
  const totalBenes = summary?.totalBeneficiaries || 1;
  const servicesPerBene = (totalServices / totalBenes).toFixed(1);

  // Group by Provider Type for chart
  const utilizationByType = Object.values(
    providers.reduce((acc: any, p) => {
      if (!acc[p.providerType]) {
        acc[p.providerType] = { providerType: p.providerType, services: 0, benes: 0 };
      }
      acc[p.providerType].services += p.totalServices;
      acc[p.providerType].benes += p.totalBeneficiaries;
      return acc;
    }, {})
  ).map((item: any) => ({
    providerType: item.providerType.length > 15 ? item.providerType.substring(0, 15) + '...' : item.providerType,
    ratio: Number((item.services / (item.benes || 1)).toFixed(1)),
    totalServices: item.services,
  }));

  // Top Utilization Providers
  const topUtilizingProviders = [...providers].sort(
    (a, b) => (b.servicesPerBeneficiary || 0) - (a.servicesPerBeneficiary || 0)
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">Utilization Analytics</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">HCPCS Volume</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mt-1">Cost & Utilization Dashboard</h1>
          <p className="text-xs text-slate-400 mt-1">
            Service volume intensity, procedure distribution, and provider utilization anomaly tracking.
          </p>
        </div>
      </div>

      <GlobalFilterBar />

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Services / Beneficiary"
          value={servicesPerBene}
          unit="Ratio"
          cmsTag="Tot_Srvcs / Tot_Benes"
          icon={TrendingUp}
          variant="accent"
          tooltip="Average number of HCPCS medical services rendered per beneficiary annually."
        />
        <KpiCard
          title="Total Services Volume"
          value={formatNumber(totalServices)}
          unit="Services"
          cmsTag="Tot_Srvcs"
          icon={Activity}
        />
        <KpiCard
          title="Attributed Beneficiaries"
          value={formatNumber(totalBenes)}
          unit="Benes"
          cmsTag="Tot_Benes"
          icon={Users}
        />
        <KpiCard
          title="Total HCPCS Categories"
          value={478}
          unit="Codes"
          cmsTag="Tot_HCPCS_Cds"
          icon={Activity}
          subtext="CMS Billing Catalog"
        />
      </div>

      {/* Utilization Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Services / Beneficiary by Specialty */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg">
          <div className="pb-3 mb-4 border-b border-slate-800">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-blue-400" />
              Services per Beneficiary by Specialty
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">Specialty utilization intensity benchmark</p>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={utilizationByType} margin={{ top: 10, right: 10, left: 10, bottom: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="providerType" stroke="#64748b" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v: number) => [`${v} Services / Bene`, 'Ratio']} />
                <Bar dataKey="ratio" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* High Volume Utilization Anomaly Provider List */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div className="pb-3 mb-3 border-b border-slate-800 flex justify-between items-center">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              High Utilization Outliers (&gt; 6.5 Ratio)
            </h2>
            <span className="text-xs font-mono text-amber-400">High Intensity</span>
          </div>

          <div className="space-y-3 flex-1 overflow-y-auto max-h-64">
            {topUtilizingProviders.map((p) => (
              <div
                key={p.npi}
                onClick={() => navigate(`/providers/${p.npi}`)}
                className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg hover:border-slate-700 cursor-pointer flex justify-between items-center transition-colors"
              >
                <div>
                  <div className="text-sm font-bold text-white">{p.providerName}</div>
                  <div className="text-xs text-slate-400">{p.providerType} • NPI: {p.npi}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-bold font-mono text-amber-400">{p.servicesPerBeneficiary} Ratio</div>
                  <div className="text-[11px] text-slate-500 font-mono">{formatNumber(p.totalServices)} services</div>
                </div>
              </div>
            ))}
          </div>

          <div className="pt-3 border-t border-slate-800 mt-2 text-right">
            <button
              onClick={() => navigate('/providers')}
              className="text-xs font-semibold text-blue-400 hover:text-blue-300 inline-flex items-center gap-1"
            >
              View All Providers <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
