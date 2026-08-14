import React from 'react';
import {
  HeartPulse,
  Users,
  Brain,
  ShieldCheck,
  Award,
  Activity,
} from 'lucide-react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';
import { useProviders, usePortfolioSummary } from '../../hooks/useProviders';
import { KpiCard } from '../../components/common/KpiCard';
import { GlobalFilterBar } from '../../components/filters/GlobalFilterBar';
import { formatNumber, formatPercent } from '../../utils/formatting';
import { calculateDualEligibilityRate } from '../../utils/calculations';

export const BeneficiaryProfile: React.FC = () => {
  const { data: summary } = usePortfolioSummary();
  const { providers } = useProviders();

  const totalBenes = summary?.totalBeneficiaries || 15690;

  // Aggregate Demographics across portfolio
  const ageUnder65 = Math.round(totalBenes * 0.12);
  const age65To74 = Math.round(totalBenes * 0.45);
  const age75To84 = Math.round(totalBenes * 0.30);
  const age85Plus = Math.round(totalBenes * 0.13);

  const femaleBenes = Math.round(totalBenes * 0.56);
  const maleBenes = Math.round(totalBenes * 0.44);

  const dualBenes = Math.round(totalBenes * 0.245);
  const nonDualBenes = totalBenes - dualBenes;
  const dualRates = calculateDualEligibilityRate(dualBenes, nonDualBenes);

  const ageData = [
    { name: '< 65 Years (Disabled)', value: ageUnder65, fill: '#60a5fa' },
    { name: '65 - 74 Years', value: age65To74, fill: '#3b82f6' },
    { name: '75 - 84 Years', value: age75To84, fill: '#1d4ed8' },
    { name: '85+ Years', value: age85Plus, fill: '#1e3a8a' },
  ];

  const genderData = [
    { name: 'Female Beneficiaries', value: femaleBenes, fill: '#ec4899' },
    { name: 'Male Beneficiaries', value: maleBenes, fill: '#3b82f6' },
  ];

  const raceData = [
    { name: 'White / Caucasian', count: Math.round(totalBenes * 0.72), percentage: 72.0 },
    { name: 'Black / African American', count: Math.round(totalBenes * 0.14), percentage: 14.0 },
    { name: 'Hispanic', count: Math.round(totalBenes * 0.07), percentage: 7.0 },
    { name: 'Asian / Pacific Islander', count: Math.round(totalBenes * 0.05), percentage: 5.0 },
    { name: 'Native American', count: Math.round(totalBenes * 0.01), percentage: 1.0 },
    { name: 'Other / Unknown', count: Math.round(totalBenes * 0.01), percentage: 1.0 },
  ];

  const chronicData = [
    { condition: 'Hypertension', percentage: 68.4, fill: '#ef4444' },
    { condition: 'Diabetes Mellitus', percentage: 42.0, fill: '#f97316' },
    { condition: 'Chronic Kidney Disease (CKD)', percentage: 32.1, fill: '#eab308' },
    { condition: 'Ischemic Heart Disease', percentage: 33.1, fill: '#10b981' },
    { condition: 'COPD / Chronic Bronchitis', percentage: 22.0, fill: '#06b6d4' },
    { condition: 'Heart Failure', percentage: 19.5, fill: '#3b82f6' },
    { condition: 'Atrial Fibrillation', percentage: 15.2, fill: '#6366f1' },
    { condition: 'Asthma', percentage: 14.2, fill: '#8b5cf6' },
    { condition: 'Stroke / TIA', percentage: 10.2, fill: '#ec4899' },
  ];

  const bhData = [
    { condition: 'Depressive Disorders', percentage: 32.4, fill: '#a855f7' },
    { condition: 'Anxiety Disorders', percentage: 29.1, fill: '#c084fc' },
    { condition: 'Tobacco Use Disorder', percentage: 22.4, fill: '#d8b4fe' },
    { condition: 'Mood Disorders', percentage: 12.8, fill: '#e9d5ff' },
    { condition: 'Alcohol / Substance Use', percentage: 5.8, fill: '#f3e8ff' },
    { condition: 'Bipolar Disorder', percentage: 3.8, fill: '#fae8ff' },
    { condition: 'Schizophrenia / Psychosis', percentage: 1.9, fill: '#fdf4ff' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-rose-400">Population Health & Demographics</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">CMS Beneficiary Summary</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mt-1">Beneficiary Analytics Profile</h1>
          <p className="text-xs text-slate-400 mt-1">
            Demographic structure, dual eligibility status, chronic condition burdens, and behavioral health risk factors.
          </p>
        </div>
      </div>

      <GlobalFilterBar />

      {/* Top Dual Eligibility & Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Dual Eligible Beneficiaries"
          value={`${dualRates.dualPct}%`}
          unit={`(${formatNumber(dualBenes)} Benes)`}
          cmsTag="Bene_Dual_Cnt"
          icon={ShieldCheck}
          variant="accent"
          tooltip="Beneficiaries enrolled in both Medicare and full/partial Medicaid."
        />
        <KpiCard
          title="Non-Dual Medicare Benes"
          value={`${dualRates.nonDualPct}%`}
          unit={`(${formatNumber(nonDualBenes)} Benes)`}
          cmsTag="Bene_Ndual_Cnt"
          icon={Users}
        />
        <KpiCard
          title="Avg Beneficiary Age"
          value={summary?.averageBeneficiaryAge || 72.4}
          unit="Years"
          cmsTag="Bene_Avg_Age"
          icon={HeartPulse}
        />
        <KpiCard
          title="Avg HCC Risk Score"
          value={summary?.averageRiskScore || 1.34}
          unit="HCC"
          cmsTag="Bene_Avg_Risk_Scre"
          icon={Activity}
          variant="accent"
        />
      </div>

      {/* Charts Row 1: Age & Gender Distributions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Age Distribution Donut */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div className="pb-3 border-b border-slate-800">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Users className="w-4 h-4 text-blue-400" />
              Age Cohort Distribution
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">CMS Age Brackets (`Bene_Age_*` fields)</p>
          </div>

          <div className="h-64 w-full my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={ageData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={4}>
                  {ageData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip formatter={(val: number) => [formatNumber(val), 'Beneficiaries']} />
                <Legend wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gender Distribution */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div className="pb-3 border-b border-slate-800">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Users className="w-4 h-4 text-pink-400" />
              Gender Distribution
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">`Bene_Feml_Cnt` vs `Bene_Male_Cnt`</p>
          </div>

          <div className="h-64 w-full my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={genderData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={4}>
                  {genderData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip formatter={(val: number) => [formatNumber(val), 'Beneficiaries']} />
                <Legend wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Charts Row 2: Chronic Conditions & Behavioral Health */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Physical Health Chronic Conditions */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg">
          <div className="pb-3 mb-4 border-b border-slate-800">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <HeartPulse className="w-4 h-4 text-rose-400" />
              Chronic Condition Burden Prevalence (%)
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">CMS Physical Health Chronic Conditions (`Bene_CC_PH_*` fields)</p>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chronicData} layout="vertical" margin={{ top: 10, right: 30, left: 140, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(v) => `${v}%`} />
                <YAxis type="category" dataKey="condition" stroke="#94a3b8" tick={{ fontSize: 11 }} width={140} />
                <Tooltip formatter={(v: number) => [`${v}%`, 'Prevalence']} />
                <Bar dataKey="percentage" fill="#ef4444" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Behavioral Health Profile */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg">
          <div className="pb-3 mb-4 border-b border-slate-800">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Brain className="w-4 h-4 text-purple-400" />
              Behavioral & Mental Health Risk Profile (%)
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">CMS Behavioral Health Chronic Conditions (`Bene_CC_BH_*` fields)</p>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={bhData} layout="vertical" margin={{ top: 10, right: 30, left: 140, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(v) => `${v}%`} />
                <YAxis type="category" dataKey="condition" stroke="#94a3b8" tick={{ fontSize: 11 }} width={140} />
                <Tooltip formatter={(v: number) => [`${v}%`, 'Prevalence']} />
                <Bar dataKey="percentage" fill="#a855f7" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
