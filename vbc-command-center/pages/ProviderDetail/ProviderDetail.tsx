import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  User,
  Users,
  MapPin,
  Building2,
  CheckCircle2,
  ShieldAlert,
  Activity,
  DollarSign,
  PieChart as PieIcon,
  HeartPulse,
  Brain,
  Sparkles,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { useProviderDetail } from '../../hooks/useProviderDetail';
import { KpiCard } from '../../components/common/KpiCard';
import { StatusBadge } from '../../components/common/StatusBadge';
import { generateProviderInsights } from '../../services/insights/insightEngine';
import { formatCurrency, formatNumber, formatPercent } from '../../utils/formatting';
import { calculateDualEligibilityRate, calculateGenderDistribution } from '../../utils/calculations';

export const ProviderDetail: React.FC = () => {
  const { npi } = useParams<{ npi: string }>();
  const navigate = useNavigate();
  const { data: provider, isLoading } = useProviderDetail(npi);

  if (isLoading) {
    return <div className="p-8 text-center text-slate-400">Loading provider performance detail...</div>;
  }

  if (!provider) {
    return (
      <div className="p-12 text-center bg-slate-900 border border-slate-800 rounded-xl space-y-4">
        <ShieldAlert className="w-12 h-12 text-rose-500 mx-auto" />
        <h2 className="text-xl font-bold text-white">Provider Record Not Found</h2>
        <p className="text-xs text-slate-400">No CMS provider match found for NPI: {npi}</p>
        <button onClick={() => navigate('/providers')} className="px-4 py-2 bg-blue-600 text-white rounded text-xs font-semibold">
          Return to Provider Explorer
        </button>
      </div>
    );
  }

  // Calculated Metrics
  const dualRates = calculateDualEligibilityRate(provider.dualEligible, provider.nonDualEligible);
  const genderRates = calculateGenderDistribution(provider.femaleBeneficiaries, provider.maleBeneficiaries);
  const insights = generateProviderInsights(provider);

  // Financial Chart Data
  const paymentVsAllowedData = [
    { metric: 'Submitted Charges', amount: provider.totalSubmittedCharges },
    { metric: 'Medicare Allowed', amount: provider.totalMedicareAllowedAmount },
    { metric: 'Medicare Payment', amount: provider.totalMedicarePaymentAmount },
    { metric: 'Standardized Payment', amount: provider.totalMedicareStandardizedAmount },
  ];

  const drugVsMedicalData = [
    { name: 'Medical Spending', value: provider.medicalMedicarePaymentAmount, fill: '#3b82f6' },
    { name: 'Drug Spending', value: provider.drugMedicarePaymentAmount, fill: '#10b981' },
  ];

  // Age Breakdown Donut
  const ageData = [
    { name: '< 65 Years', count: provider.ageUnder65, fill: '#60a5fa' },
    { name: '65 - 74 Years', count: provider.age65To74, fill: '#3b82f6' },
    { name: '75 - 84 Years', count: provider.age75To84, fill: '#1d4ed8' },
    { name: '85+ Years', count: provider.age85Plus, fill: '#1e3a8a' },
  ];

  // Chronic Conditions Horizontal Bar Data
  const chronicData = Object.entries(provider.chronicConditions).map(([key, value]) => ({
    condition: key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1'),
    percentage: value,
  })).sort((a, b) => b.percentage - a.percentage);

  // Behavioral Health Horizontal Bar Data
  const bhData = Object.entries(provider.behavioralHealth).map(([key, value]) => ({
    condition: key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1'),
    percentage: value,
  })).sort((a, b) => b.percentage - a.percentage);

  return (
    <div className="space-y-6">
      {/* Back Button & Header */}
      <div>
        <button
          onClick={() => navigate('/providers')}
          className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-blue-400 font-medium mb-3 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Provider Explorer
        </button>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono px-2 py-0.5 bg-slate-800 text-blue-400 rounded border border-slate-700">
                NPI: {provider.npi}
              </span>
              <StatusBadge status={provider.performanceTier || 'Moderate'} />
              {provider.medicareParticipating && (
                <span className="text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded font-mono">
                  ● Medicare Participating
                </span>
              )}
            </div>

            <h1 className="text-2xl font-bold text-white mt-1.5">{provider.providerName}</h1>

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 mt-1">
              <span>Type: <strong className="text-slate-200">{provider.providerType}</strong></span>
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-500" />
                {provider.city}, {provider.state} {provider.zipCode}
              </span>
              <span>Entity: <strong className="text-slate-200">{provider.entityCode === 'I' ? 'Individual Physician' : 'Organization'}</strong></span>
            </div>
          </div>

          <div className="bg-slate-950/80 border border-slate-800 p-3 rounded-lg flex items-center gap-4 text-xs">
            <div>
              <span className="text-slate-500 block">Services / Bene Ratio</span>
              <span className="text-lg font-bold font-mono text-blue-400">{provider.servicesPerBeneficiary}</span>
            </div>
            <div className="border-l border-slate-800 pl-4">
              <span className="text-slate-500 block">Avg HCC Risk Score</span>
              <span className={`text-lg font-bold font-mono ${provider.averageRiskScore > 1.4 ? 'text-rose-400' : 'text-emerald-400'}`}>
                {provider.averageRiskScore}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* KPI Metrics Cards (7 Cards) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        <KpiCard title="Beneficiaries" value={formatNumber(provider.totalBeneficiaries)} cmsTag="Tot_Benes" />
        <KpiCard title="Total Services" value={formatNumber(provider.totalServices)} cmsTag="Tot_Srvcs" />
        <KpiCard title="Submitted Charge" value={formatCurrency(provider.totalSubmittedCharges)} cmsTag="Tot_Sbmtd_Chrg" />
        <KpiCard title="Medicare Allowed" value={formatCurrency(provider.totalMedicareAllowedAmount)} cmsTag="Tot_Mdcr_Alowd_Amt" />
        <KpiCard title="Medicare Payment" value={formatCurrency(provider.totalMedicarePaymentAmount)} cmsTag="Tot_Mdcr_Pymt_Amt" variant="accent" />
        <KpiCard title="Standardized" value={formatCurrency(provider.totalMedicareStandardizedAmount)} cmsTag="Tot_Mdcr_Stdzd_Amt" />
        <KpiCard title="Avg Age" value={provider.averageBeneficiaryAge} unit="Yrs" cmsTag="Bene_Avg_Age" />
      </div>

      {/* Section 1: Cost & Financial Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Medicare Payment vs Allowed vs Submitted (2 Cols) */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg">
          <div className="pb-3 mb-4 border-b border-slate-800 flex justify-between items-center">
            <div>
              <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-emerald-400" />
                Medicare Payment vs Allowed vs Submitted Charge Breakdown
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">CMS Provider payment metrics visualization</p>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={paymentVsAllowedData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="metric" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(v) => `$${(v / 1000000).toFixed(1)}M`} />
                <Tooltip formatter={(v: number) => formatCurrency(v, false)} />
                <Bar dataKey="amount" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Drug vs Medical Spending (1 Col) */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div className="pb-3 border-b border-slate-800">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Drug vs Medical Spending</h2>
            <p className="text-xs text-slate-400 mt-0.5">Part B Drug vs Medical Services split</p>
          </div>

          <div className="h-48 w-full my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={drugVsMedicalData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={4}>
                  {drugVsMedicalData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip formatter={(v: number) => formatCurrency(v, false)} />
                <Legend wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg text-xs space-y-1 font-mono">
            <div className="flex justify-between">
              <span className="text-slate-400">Medical Services:</span>
              <span className="text-blue-400 font-bold">{formatCurrency(provider.medicalMedicarePaymentAmount)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Part B Drug Spend:</span>
              <span className="text-emerald-400 font-bold">{formatCurrency(provider.drugMedicarePaymentAmount)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Section 2: Beneficiary Demographics & Risk Profile */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Dual Eligibility & Demographics (1 Col) */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div className="pb-3 border-b border-slate-800">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Users className="w-4 h-4 text-blue-400" />
              Dual Eligibility & Demographics
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">Medicare & Medicaid dual-eligible status</p>
          </div>

          <div className="space-y-4 my-3 text-xs">
            {/* Dual Eligibility Card */}
            <div className="p-3.5 bg-slate-950 border border-slate-800 rounded-lg space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-semibold text-slate-200">Dual Eligible Beneficiaries</span>
                <span className="font-mono text-xs px-2 py-0.5 bg-blue-950 text-blue-300 rounded border border-blue-800">
                  {dualRates.dualPct}% Dual Rate
                </span>
              </div>

              <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden flex">
                <div style={{ width: `${dualRates.dualPct}%` }} className="bg-blue-500 h-full" title="Dual Eligible" />
                <div style={{ width: `${dualRates.nonDualPct}%` }} className="bg-slate-600 h-full" title="Non-Dual" />
              </div>

              <div className="flex justify-between text-[11px] text-slate-400 font-mono">
                <span>Dual: {provider.dualEligible} benes</span>
                <span>Non-Dual: {provider.nonDualEligible} benes</span>
              </div>
            </div>

            {/* Gender Split Card */}
            <div className="p-3.5 bg-slate-950 border border-slate-800 rounded-lg space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-semibold text-slate-200">Gender Distribution</span>
                <span className="font-mono text-xs text-slate-400">
                  F: {genderRates.femalePct}% | M: {genderRates.malePct}%
                </span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden flex">
                <div style={{ width: `${genderRates.femalePct}%` }} className="bg-pink-500 h-full" />
                <div style={{ width: `${genderRates.malePct}%` }} className="bg-blue-500 h-full" />
              </div>
            </div>
          </div>

          <div className="text-[11px] text-slate-500">
            Source: CMS Beneficiary Summary File (`Bene_Dual_Cnt` / `Bene_Ndual_Cnt`)
          </div>
        </div>

        {/* Chronic Conditions Burden (1 Col) */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg">
          <div className="pb-3 mb-3 border-b border-slate-800">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <HeartPulse className="w-4 h-4 text-rose-400" />
              Chronic Condition Burden Prevalence (%)
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">Physical health chronic conditions</p>
          </div>

          <div className="space-y-2.5 text-xs">
            {chronicData.slice(0, 6).map((item) => (
              <div key={item.condition} className="space-y-1">
                <div className="flex justify-between text-slate-300 font-medium">
                  <span>{item.condition}</span>
                  <span className="font-mono text-rose-400">{item.percentage}%</span>
                </div>
                <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden">
                  <div style={{ width: `${Math.min(item.percentage, 100)}%` }} className="bg-rose-500 h-full rounded-full" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Behavioral Health Profile (1 Col) */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg">
          <div className="pb-3 mb-3 border-b border-slate-800">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Brain className="w-4 h-4 text-purple-400" />
              Behavioral Health Risk Profile (%)
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">Mental & behavioral health prevalence</p>
          </div>

          <div className="space-y-2.5 text-xs">
            {bhData.slice(0, 6).map((item) => (
              <div key={item.condition} className="space-y-1">
                <div className="flex justify-between text-slate-300 font-medium">
                  <span>{item.condition}</span>
                  <span className="font-mono text-purple-400">{item.percentage}%</span>
                </div>
                <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden">
                  <div style={{ width: `${Math.min(item.percentage * 2, 100)}%` }} className="bg-purple-500 h-full rounded-full" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Section 3: AI Provider Insights */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg">
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-400" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">AI Insights & Anomaly Analysis</h2>
            <span className="text-[10px] font-mono px-2 py-0.5 bg-blue-950 text-blue-300 rounded border border-blue-800">
              Demo AI Insight
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {insights.map((insight) => (
            <div key={insight.id} className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-2.5 text-xs">
              <div className="flex justify-between items-start">
                <span className="font-bold text-white text-sm">{insight.title}</span>
                <span className="px-2 py-0.5 bg-slate-800 text-slate-300 font-mono text-[10px] rounded">{insight.impactEstimate}</span>
              </div>

              <p className="text-slate-300 leading-relaxed">{insight.summary}</p>

              <div className="pt-2 border-t border-slate-800/80">
                <span className="text-slate-400 font-semibold block mb-1">Potential Cost & Risk Drivers:</span>
                <ul className="list-disc list-inside space-y-0.5 text-slate-400">
                  {insight.potentialDrivers.map((driver, idx) => (
                    <li key={idx}>{driver}</li>
                  ))}
                </ul>
              </div>

              <div className="p-2 bg-blue-950/40 border border-blue-900/60 rounded text-blue-300">
                <strong>Suggested Investigation:</strong> {insight.suggestedAction}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
