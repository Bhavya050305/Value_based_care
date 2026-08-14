import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BarChart3,
  TrendingUp,
  Award,
  AlertTriangle,
  ArrowRight,
  SlidersHorizontal,
} from 'lucide-react';
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  CartesianGrid,
  Cell,
  BarChart,
  Bar,
  Legend,
} from 'recharts';
import { useProviders } from '../../hooks/useProviders';
import { GlobalFilterBar } from '../../components/filters/GlobalFilterBar';
import { StatusBadge } from '../../components/common/StatusBadge';
import { formatCurrency, formatNumber } from '../../utils/formatting';

export const PerformanceAnalytics: React.FC = () => {
  const navigate = useNavigate();
  const { providers, isLoading } = useProviders();

  const scatterData = providers.map((p) => ({
    name: p.providerName,
    npi: p.npi,
    riskScore: p.averageRiskScore,
    paymentPerBene: p.totalMedicarePaymentAmount / (p.totalBeneficiaries || 1),
    totalPayment: p.totalMedicarePaymentAmount,
    tier: p.performanceTier,
  }));

  const variationData = providers.map((p) => ({
    name: p.lastNameOrg.substring(0, 15),
    npi: p.npi,
    servicesPerBene: p.servicesPerBeneficiary,
    paymentPerBene: p.paymentPerBeneficiary,
    riskScore: p.averageRiskScore,
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">Payer Value Analytics</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">Peer Variation</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mt-1">Provider Performance Analytics</h1>
          <p className="text-xs text-slate-400 mt-1">
            Analyze provider cost variation, risk-adjusted payment efficiency, and benchmark outlier clusters.
          </p>
        </div>
      </div>

      {/* Global Filters */}
      <GlobalFilterBar />

      {/* Variation Chart Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scatter Chart: Risk Score vs Payment per Beneficiary */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg">
          <div className="pb-3 mb-4 border-b border-slate-800">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-blue-400" />
              Risk Score vs Medicare Payment per Beneficiary
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">Top-right quadrant indicates high risk & high cost providers</p>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" dataKey="riskScore" name="Risk Score" unit=" HCC" stroke="#64748b" domain={[0.8, 2.0]} tick={{ fontSize: 11 }} />
                <YAxis type="number" dataKey="paymentPerBene" name="Payment / Bene" stroke="#64748b" tickFormatter={(v) => `$${v}`} tick={{ fontSize: 11 }} />
                <ZAxis type="number" dataKey="totalPayment" range={[60, 400]} />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ payload }) => {
                    if (payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-slate-900 border border-slate-700 p-2.5 rounded-lg shadow-xl text-xs space-y-1">
                          <div className="font-bold text-white">{data.name}</div>
                          <div className="text-slate-400">Risk Score: <strong className="text-white">{data.riskScore} HCC</strong></div>
                          <div className="text-slate-400">Payment / Bene: <strong className="text-emerald-400">{formatCurrency(data.paymentPerBene)}</strong></div>
                          <div className="text-slate-400">Total Payment: <strong className="text-blue-400">{formatCurrency(data.totalPayment)}</strong></div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter data={scatterData}>
                  {scatterData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.tier === 'High Performance' ? '#059669' : entry.tier === 'Needs Attention' ? '#dc2626' : '#d97706'}
                    />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bar Chart: Services per Beneficiary Variation */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg">
          <div className="pb-3 mb-4 border-b border-slate-800">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-emerald-400" />
              Services per Beneficiary Variation
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">Utilization intensity per beneficiary across providers</p>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={variationData} margin={{ top: 10, right: 10, left: 10, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v: number) => [`${v} Services`, 'Services / Bene']} />
                <Bar dataKey="servicesPerBene" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Provider Variation Ranking Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950/60">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">Provider Peer Variation Analysis</h2>
          <span className="text-xs font-mono text-slate-400">{providers.length} Providers Evaluated</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="p-3.5">Provider Name</th>
                <th className="p-3.5 text-right">Beneficiaries</th>
                <th className="p-3.5 text-right">Medicare Payment</th>
                <th className="p-3.5 text-right">Allowed Amount</th>
                <th className="p-3.5 text-right">Payment / Bene</th>
                <th className="p-3.5 text-right">Services / Bene</th>
                <th className="p-3.5 text-right">Risk Score</th>
                <th className="p-3.5 text-center">Performance Tier</th>
                <th className="p-3.5 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {providers.map((p) => (
                <tr key={p.npi} className="hover:bg-slate-800/50 transition-colors">
                  <td className="p-3.5 font-medium text-white">
                    <div className="font-semibold text-slate-200">{p.providerName}</div>
                    <div className="text-[11px] font-mono text-slate-400">NPI: {p.npi} • {p.providerType}</div>
                  </td>
                  <td className="p-3.5 text-right font-mono text-slate-200">{formatNumber(p.totalBeneficiaries)}</td>
                  <td className="p-3.5 text-right font-mono font-bold text-emerald-400">{formatCurrency(p.totalMedicarePaymentAmount)}</td>
                  <td className="p-3.5 text-right font-mono text-slate-300">{formatCurrency(p.totalMedicareAllowedAmount)}</td>
                  <td className="p-3.5 text-right font-mono text-slate-200">{formatCurrency(p.paymentPerBeneficiary || 0)}</td>
                  <td className="p-3.5 text-right font-mono font-semibold text-blue-400">{p.servicesPerBeneficiary}</td>
                  <td className="p-3.5 text-right font-mono font-semibold text-slate-200">{p.averageRiskScore}</td>
                  <td className="p-3.5 text-center">
                    <StatusBadge status={p.performanceTier || 'Moderate'} size="sm" />
                  </td>
                  <td className="p-3.5 text-center">
                    <button
                      onClick={() => navigate(`/providers/${p.npi}`)}
                      className="px-2.5 py-1 text-[11px] bg-blue-600/20 hover:bg-blue-600 text-blue-300 hover:text-white rounded border border-blue-500/30 transition-colors"
                    >
                      Drilldown
                    </button>
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
