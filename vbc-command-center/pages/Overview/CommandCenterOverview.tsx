import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  HeartPulse,
  DollarSign,
  ReceiptText,
  Activity,
  Calendar,
  Sparkles,
  TrendingUp,
  Building2,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
  Cell,
} from 'recharts';
import { KpiCard } from '../../components/common/KpiCard';
import { GlobalFilterBar } from '../../components/filters/GlobalFilterBar';
import { MetricSkeleton } from '../../components/common/MetricSkeleton';
import { useProviders, usePortfolioSummary, useHistoricalTrends } from '../../hooks/useProviders';
import { formatCurrency, formatNumber } from '../../utils/formatting';

export const CommandCenterOverview: React.FC = () => {
  const navigate = useNavigate();
  const { data: summary, isLoading: loadingSummary } = usePortfolioSummary();
  const { data: trends, isLoading: loadingTrends } = useHistoricalTrends();
  const { providers } = useProviders();

  // Calculate Provider Performance Distribution dynamically using calculateProviderPerformance rules
  const highPerfCount = providers.filter((p) => p.performanceTier === 'High Performance').length;
  const modPerfCount = providers.filter((p) => p.performanceTier === 'Moderate').length;
  const needsAttnCount = providers.filter((p) => p.performanceTier === 'Needs Attention').length;

  const distributionData = [
    { category: 'High Performance', count: highPerfCount, fill: '#059669' },
    { category: 'Moderate Watch', count: modPerfCount, fill: '#d97706' },
    { category: 'Needs Attention', count: needsAttnCount, fill: '#dc2626' },
  ];

  return (
    <div className="space-y-6 font-sans">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800/80 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">
              Value-Based Care Contract Performance
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-800/80 font-mono">
              ● DEMO DATA
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mt-1">
            Command Center Overview
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Enterprise view of value-based care performance, cost, quality, utilization and beneficiary risk.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg">
          <Calendar className="w-4 h-4 text-blue-400" />
          <span>Last Updated: <strong className="text-slate-200 font-mono">Aug 13, 2026</strong></span>
        </div>
      </div>

      {/* Global Filter Bar */}
      <GlobalFilterBar />

      {/* Performance Snapshot Section (KPI Grid) */}
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-blue-400" /> Performance Snapshot
          </h2>
          <span className="text-xs text-slate-500 font-mono">CMS Dataset API Normalized</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {loadingSummary ? (
            Array.from({ length: 8 }).map((_, i) => <MetricSkeleton key={i} />)
          ) : (
            <>
              <KpiCard
                title="Total Providers"
                value={formatNumber(summary?.totalProviders || 0, false)}
                unit="NPIs"
                cmsTag="Rndrng_NPI"
                changePct={summary?.beneficiariesChangePct}
                icon={Users}
                tooltip="Unique rendering providers (NPIs) actively billing under value-based contracts."
              />
              <KpiCard
                title="Total Beneficiaries"
                value={formatNumber(summary?.totalBeneficiaries || 0)}
                unit="Benes"
                cmsTag="Tot_Benes"
                changePct={summary?.beneficiariesChangePct}
                icon={HeartPulse}
                tooltip="Total unique Medicare beneficiaries assigned to network providers."
                variant="accent"
              />
              <KpiCard
                title="Medicare Payments"
                value={formatCurrency(summary?.totalMedicarePayments || 0)}
                cmsTag="Tot_Mdcr_Pymt_Amt"
                changePct={summary?.paymentChangePct}
                icon={DollarSign}
                tooltip="Actual net Medicare payments reimbursed to rendering providers."
                variant="accent"
              />
              <KpiCard
                title="Medicare Allowed Amount"
                value={formatCurrency(summary?.totalMedicareAllowed || 0)}
                cmsTag="Tot_Mdcr_Alowd_Amt"
                changePct={summary?.allowedChangePct}
                icon={ReceiptText}
                tooltip="Total Medicare allowed charges after fee schedule adjustments."
              />
              <KpiCard
                title="Total Services"
                value={formatNumber(summary?.totalServices || 0)}
                unit="Services"
                cmsTag="Tot_Srvcs"
                changePct={summary?.servicesChangePct}
                icon={Activity}
                tooltip="Total volume of HCPCS line-item medical services rendered."
              />
              <KpiCard
                title="Average Beneficiary Age"
                value={summary?.averageBeneficiaryAge || 72.4}
                unit="Years"
                cmsTag="Bene_Avg_Age"
                subtext="Demographics"
                icon={Users}
                tooltip="Mean beneficiary age across active attributed patient panel."
              />
              <KpiCard
                title="Average Risk Score"
                value={summary?.averageRiskScore || 1.34}
                unit="HCC"
                cmsTag="Bene_Avg_Risk_Scre"
                changePct={summary?.riskScoreChangePct}
                icon={TrendingUp}
                tooltip="Hierarchical Condition Category (HCC) risk adjustment score (National baseline = 1.00)."
                variant={summary && summary.averageRiskScore > 1.3 ? 'warning' : 'default'}
              />
              <KpiCard
                title="Medicare Standardized Amount"
                value={formatCurrency(summary?.totalStandardizedAmount || 0)}
                cmsTag="Tot_Mdcr_Stdzd_Amt"
                subtext="Geographic Normalization"
                icon={DollarSign}
                tooltip="Payment amount normalized to remove geographic wage index and GPCI variations."
              />
            </>
          )}
        </div>
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Cost & Payment Trends Chart (2 Cols) */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 mb-4 border-b border-slate-800/80 gap-2">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                Cost & Payment Trends
                <span className="text-[10px] font-mono px-2 py-0.5 bg-slate-800 text-slate-400 rounded">
                  Demo Historical Trend
                </span>
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Comparison of Medicare Allowed Amount vs Medicare Payment Amount vs Standardized Payment.
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs font-mono">
              <span className="flex items-center text-blue-400"><span className="w-2.5 h-2.5 rounded-full bg-blue-500 mr-1.5" /> Allowed</span>
              <span className="flex items-center text-emerald-400"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500 mr-1.5" /> Paid</span>
            </div>
          </div>

          <div className="h-72 w-full">
            {loadingTrends ? (
              <div className="h-full flex items-center justify-center text-slate-500 text-xs">Loading trends...</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trends} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorAllowed" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                    </linearGradient>
                    <linearGradient id="colorPayment" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="year" stroke="#64748b" tick={{ fontSize: 12 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(val) => `$${(val / 1000000).toFixed(0)}M`} />
                  <Tooltip formatter={(val: number) => formatCurrency(val, false)} />
                  <Area type="monotone" dataKey="allowedAmount" name="Medicare Allowed" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorAllowed)" />
                  <Area type="monotone" dataKey="paymentAmount" name="Medicare Payment" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorPayment)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Provider Performance Distribution Bar Chart (1 Col) */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col">
          <div className="pb-3 mb-4 border-b border-slate-800/80">
            <h2 className="text-base font-bold text-white">Provider Performance Distribution</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Providers categorized by risk score and utilization rules (<code className="text-blue-400">calculateProviderPerformance</code>).
            </p>
          </div>

          <div className="h-56 w-full flex-1">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={distributionData} layout="vertical" margin={{ top: 10, right: 20, left: 20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="category" stroke="#94a3b8" tick={{ fontSize: 11 }} width={110} />
                <Tooltip formatter={(val: number) => [`${val} Providers`, 'Volume']} />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {distributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="pt-3 border-t border-slate-800 mt-2 flex items-center justify-between text-xs">
            <span className="text-slate-400">Action Required:</span>
            <button
              onClick={() => navigate('/providers')}
              className="text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1"
            >
              Explore Providers ({providers.length}) <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Quick Action Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div
          onClick={() => navigate('/alerts')}
          className="bg-slate-900/60 border border-slate-800/90 hover:border-rose-500/50 p-4 rounded-xl cursor-pointer transition-all group flex items-start gap-3.5"
        >
          <div className="p-2.5 bg-rose-950/80 border border-rose-800/80 rounded-lg text-rose-400 group-hover:scale-105 transition-transform">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white group-hover:text-rose-400 transition-colors">Alerts & Attention</h3>
            <p className="text-xs text-slate-400 mt-1">Review 5 critical payment variance & high utilization warnings.</p>
          </div>
        </div>

        <div
          onClick={() => navigate('/simulator')}
          className="bg-slate-900/60 border border-slate-800/90 hover:border-blue-500/50 p-4 rounded-xl cursor-pointer transition-all group flex items-start gap-3.5"
        >
          <div className="p-2.5 bg-blue-950/80 border border-blue-800/80 rounded-lg text-blue-400 group-hover:scale-105 transition-transform">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white group-hover:text-blue-400 transition-colors">What-If Scenario Simulator</h3>
            <p className="text-xs text-slate-400 mt-1">Model payment savings by adjusting service utilization levels.</p>
          </div>
        </div>

        <div
          onClick={() => navigate('/acos')}
          className="bg-slate-900/60 border border-slate-800/90 hover:border-emerald-500/50 p-4 rounded-xl cursor-pointer transition-all group flex items-start gap-3.5"
        >
          <div className="p-2.5 bg-emerald-950/80 border border-emerald-800/80 rounded-lg text-emerald-400 group-hover:scale-105 transition-transform">
            <Building2 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white group-hover:text-emerald-400 transition-colors">ACO Shared Savings Explorer</h3>
            <p className="text-xs text-slate-400 mt-1">Evaluate 5 Medicare Shared Savings Program contracts.</p>
          </div>
        </div>
      </div>
    </div>
  );
};
