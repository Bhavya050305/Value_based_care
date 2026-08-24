import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDataMode } from '../context/DataModeContext';
import { usePageAIContext } from '../hooks/usePageAIContext';
import { acoService } from '../services/acoService';
import { analyticsService } from '../services/analyticsService';
import { ACO } from '../types';
import { PortfolioSummary, FinancialTrendPoint } from '../data/mock/financialData';
import { Layout } from '../components/Layout';
import { KPIcard } from '../components/KPIcard';
import { StatusBadge } from '../components/StatusBadge';
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import {
  Activity,
  TrendingUp,
  FolderHeart,
  Search,
  ChevronRight,
  ShieldCheck,
  AlertOctagon,
  ShieldAlert,
  Wallet
} from 'lucide-react';

import { useACO } from '../context/ACOContext';

type RiskFilter = 'ALL' | 'LOW' | 'MEDIUM' | 'HIGH';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { dataMode } = useDataMode();
  const { selectedYear, setSelectedYear, supportedYears } = useACO();

  const [acos, setAcos] = useState<ACO[]>([]);
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [trends, setTrends] = useState<FinancialTrendPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [chartViewMode, setChartViewMode] = useState<'year' | 'trend'>('year');

  // Filters state
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState<RiskFilter>('ALL');

  // Paging state
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [acoResponse, summaryResponse, trendResponse] = await Promise.all([
          acoService.getACOs(dataMode, selectedYear),
          analyticsService.getPortfolioSummary(dataMode, selectedYear),
          analyticsService.getPortfolioFinancialTrend(dataMode)
        ]);

        if (acoResponse.success) setAcos(acoResponse.data);
        else setAcos([]);
        
        if (summaryResponse.success) setSummary(summaryResponse.data);
        else setSummary(null);

        if (trendResponse.success) setTrends(trendResponse.data);
        else setTrends([]);
      } catch (err) {
        console.error('Dashboard data load error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [dataMode, selectedYear]);

  const filteredAcos = acos.filter((aco) => {
    const matchesSearch = aco.name.toLowerCase().includes(search.toLowerCase()) || aco.id.toLowerCase().includes(search.toLowerCase());
    const matchesRisk = riskFilter === 'ALL' || aco.riskLevel === riskFilter;
    return matchesSearch && matchesRisk;
  });

  const totalPages = Math.ceil(filteredAcos.length / itemsPerPage) || 1;
  const pagedAcos = filteredAcos.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const goodCount = summary?.goodStanding ?? acos.filter(a => a.riskLevel === 'LOW').length;
  const attentionCount = summary?.needsAttention ?? acos.filter(a => a.riskLevel === 'MEDIUM').length;
  const riskCount = summary?.atRisk ?? acos.filter(a => a.riskLevel === 'HIGH').length;
  const totalCount = summary?.totalACOs ?? acos.length;

  const totalSav = summary?.totalSavings ?? 0;
  const totalExp = summary?.totalExpenditure ?? 0;
  const totalBench = summary?.riskAdjustedBenchmark ?? 0;

  const savingsRatePercent = totalExp > 0 ? ((totalSav / totalExp) * 100).toFixed(2) : '0.00';

  const riskPieData = [
    { name: 'Good Standing', value: goodCount, color: '#10B981' },
    { name: 'Needs Attention', value: attentionCount, color: '#F97316' },
    { name: 'At Risk', value: riskCount, color: '#EF4444' }
  ];

  const expenditureChartData = summary
    ? [
        {
          name: 'Benchmark Expenditure',
          shortName: 'Benchmark Target',
          value: totalBench,
          formatted: `$${(totalBench / 1e9).toFixed(2)}B`,
          fill: '#3B82F6',
        },
        {
          name: 'Actual Expenditure',
          shortName: 'Actual Spend',
          value: totalExp,
          formatted: `$${(totalExp / 1e9).toFixed(2)}B`,
          fill: '#475569',
        },
        {
          name: totalSav >= 0 ? 'Gross Savings' : 'Gross Loss',
          shortName: totalSav >= 0 ? 'Gross Savings' : 'Gross Loss',
          value: totalSav,
          formatted:
            Math.abs(totalSav) >= 1e9
              ? `$${(totalSav / 1e9).toFixed(2)}B`
              : `$${(totalSav / 1e6).toFixed(1)}M`,
          fill: totalSav >= 0 ? '#10B981' : '#EF4444',
        },
      ]
    : [];

  const handleRiskCardClick = (level: RiskFilter) => {
    setCurrentPage(1);
    setRiskFilter((prev) => (prev === level ? 'ALL' : level));
    document.getElementById('aco-table')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  usePageAIContext(
    {
      page: 'Portfolio Overview',
      route: '/dashboard',
      year: selectedYear,
      riskFilter,
      visibleKPIs: summary,
      visibleACOCount: filteredAcos.length
    },
    [totalCount, riskFilter, filteredAcos.length]
  );

  return (
    <Layout title="Value-Based Care Contract Performance Command Center" onLogout={() => {}}>
      {/* Portfolio KPI cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPIcard
          title="Total ACOs"
          value={totalCount}
          subtext="Value-Based Contracts"
          icon={<FolderHeart size={18} />}
          loading={loading}
        />
        <button onClick={() => handleRiskCardClick('LOW')} className="text-left">
          <KPIcard
            title="Good Standing"
            value={goodCount}
            subtext="Low Risk ACOs"
            icon={<ShieldCheck size={18} />}
            loading={loading}
            highlight={riskFilter === 'LOW'}
            accent="green"
          />
        </button>
        <button onClick={() => handleRiskCardClick('MEDIUM')} className="text-left">
          <KPIcard
            title="Needs Attention"
            value={attentionCount}
            subtext="Moderate Risk ACOs"
            icon={<ShieldAlert size={18} />}
            loading={loading}
            highlight={riskFilter === 'MEDIUM'}
            accent="orange"
          />
        </button>
        <button onClick={() => handleRiskCardClick('HIGH')} className="text-left">
          <KPIcard
            title="At Risk"
            value={riskCount}
            subtext="High Risk ACOs"
            icon={<AlertOctagon size={18} />}
            loading={loading}
            highlight={riskFilter === 'HIGH'}
            accent="red"
          />
        </button>
      </div>

      {/* Financial Performance KPI Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
        <div className="bg-white rounded-xl border border-vbc-gray-light p-4 shadow-card">
          <div className="flex items-center space-x-2 text-vbc-gray text-xs font-semibold">
            <Wallet size={16} className="text-vbc-blue" />
            <span>Benchmark Spend</span>
          </div>
          <div className="text-xl font-bold text-vbc-navy mt-1">
            {loading ? '...' : `$${(totalBench / 1e9).toFixed(2)}B`}
          </div>
          <span className="text-[10px] text-vbc-gray">Performance Year {selectedYear} Target</span>
        </div>

        <div className="bg-white rounded-xl border border-vbc-gray-light p-4 shadow-card">
          <div className="flex items-center space-x-2 text-vbc-gray text-xs font-semibold">
            <Activity size={16} className="text-vbc-blue" />
            <span>Actual Spend</span>
          </div>
          <div className="text-xl font-bold text-vbc-navy mt-1">
            {loading ? '...' : `$${(totalExp / 1e9).toFixed(2)}B`}
          </div>
          <span className="text-[10px] text-vbc-gray">Cumulative Expenditure</span>
        </div>

        <div className="bg-white rounded-xl border border-vbc-gray-light p-4 shadow-card">
          <div className="flex items-center space-x-2 text-vbc-gray text-xs font-semibold">
            <TrendingUp size={16} className="text-vbc-green" />
            <span>Net Gross Savings</span>
          </div>
          <div className="text-xl font-bold text-vbc-green-dark mt-1">
            {loading ? '...' : `$${(totalSav / 1e6).toFixed(1)}M`}
          </div>
          <span className="text-[10px] text-vbc-green font-semibold">({savingsRatePercent}% Savings Rate)</span>
        </div>

        <div className="bg-white rounded-xl border border-vbc-gray-light p-4 shadow-card">
          <div className="flex items-center space-x-2 text-vbc-gray text-xs font-semibold">
            <ShieldCheck size={16} className="text-vbc-blue" />
            <span>Active Performance Year</span>
          </div>
          <div className="text-xl font-bold text-vbc-navy mt-1">
            PY {selectedYear}
          </div>
          <span className="text-[10px] text-vbc-gray">CMS Data Sync Active</span>
        </div>
      </div>

      {/* Visual Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        {/* Risk Distribution Donut */}
        <div className="bg-white rounded-xl border border-vbc-gray-light p-5 shadow-card flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-sm text-vbc-navy">Contract Risk Profile</h3>
            <p className="text-xs text-vbc-gray mt-0.5">Distribution of {totalCount} ACOs by performance status</p>
          </div>

          <div className="h-48 my-2">
            {loading ? (
              <div className="h-full flex items-center justify-center text-xs text-vbc-gray">Loading chart...</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {riskPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: any) => [`${value} ACOs`, 'Contracts']} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="grid grid-cols-3 gap-2 pt-2 border-t border-vbc-gray-light text-center">
            <div>
              <span className="text-[10px] text-vbc-gray block font-semibold">Good</span>
              <span className="text-sm font-bold text-vbc-green-dark">{goodCount}</span>
            </div>
            <div>
              <span className="text-[10px] text-vbc-gray block font-semibold">Attention</span>
              <span className="text-sm font-bold text-vbc-orange-dark">{attentionCount}</span>
            </div>
            <div>
              <span className="text-[10px] text-vbc-gray block font-semibold">At Risk</span>
              <span className="text-sm font-bold text-vbc-red-dark">{riskCount}</span>
            </div>
          </div>
        </div>

        {/* Portfolio Savings & Expenditure Graph (Dynamic for selected Performance Year) */}
        <div className="bg-white rounded-xl border border-vbc-gray-light p-5 shadow-card lg:col-span-2 flex flex-col justify-between">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h3 className="font-bold text-sm text-vbc-navy">
                {chartViewMode === 'year'
                  ? `Expenditure & Savings | Performance Year: ${selectedYear}`
                  : 'Multi-Year Portfolio Financial Trend (2022–2024)'}
              </h3>
              <p className="text-xs text-vbc-gray mt-0.5">
                {chartViewMode === 'year'
                  ? `Aggregated CMS benchmark vs actual expenditure for PY ${selectedYear}`
                  : 'Multi-year aggregated CMS benchmark vs actual expenditure ($ Billions / $ Millions)'}
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <div className="bg-gray-100 p-0.5 rounded-lg flex items-center border border-vbc-gray-light text-[11px] font-semibold">
                <button
                  onClick={() => setChartViewMode('year')}
                  className={`px-2.5 py-1 rounded-md transition-colors ${
                    chartViewMode === 'year'
                      ? 'bg-white text-vbc-navy shadow-sm font-bold'
                      : 'text-vbc-gray hover:text-vbc-navy'
                  }`}
                >
                  PY {selectedYear} Breakdown
                </button>
                <button
                  onClick={() => setChartViewMode('trend')}
                  className={`px-2.5 py-1 rounded-md transition-colors ${
                    chartViewMode === 'trend'
                      ? 'bg-white text-vbc-navy shadow-sm font-bold'
                      : 'text-vbc-gray hover:text-vbc-navy'
                  }`}
                >
                  Multi-Year Trend
                </button>
              </div>

              <div className="text-xs font-semibold text-vbc-blue bg-vbc-blue-light/50 px-2.5 py-1 rounded-lg">
                PY {selectedYear} Active
              </div>
            </div>
          </div>

          <div className="h-64 my-2">
            {loading ? (
              <div className="h-full flex items-center justify-center text-xs text-vbc-gray">
                Loading expenditure data for PY {selectedYear}...
              </div>
            ) : chartViewMode === 'year' ? (
              !summary ? (
                <div className="h-full flex items-center justify-center text-xs text-red-500 font-semibold">
                  Unable to load expenditure data for PY {selectedYear}.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={expenditureChartData} margin={{ top: 25, right: 30, left: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                    <XAxis dataKey="shortName" tick={{ fontSize: 11, fill: '#64748B', fontWeight: 600 }} />
                    <YAxis
                      tick={{ fontSize: 11, fill: '#64748B' }}
                      tickFormatter={(v) => {
                        const abs = Math.abs(v);
                        if (abs >= 1e9) return `$${(v / 1e9).toFixed(1)}B`;
                        if (abs >= 1e6) return `$${(v / 1e6).toFixed(0)}M`;
                        return `$${v}`;
                      }}
                    />
                    <Tooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const d = payload[0].payload;
                          return (
                            <div className="bg-white p-3 border border-vbc-gray-light rounded-xl shadow-lg text-xs space-y-1">
                              <p className="font-bold text-vbc-navy">{d.name}</p>
                              <p className="text-sm font-extrabold" style={{ color: d.fill }}>
                                {d.formatted}
                              </p>
                              <p className="text-[10px] text-vbc-gray">Performance Year: {selectedYear}</p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Bar dataKey="value" radius={[6, 6, 0, 0]} barSize={50}>
                      {expenditureChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trends} margin={{ top: 10, right: 15, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                  <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#64748B' }} />
                  <YAxis
                    yAxisId="left"
                    orientation="left"
                    domain={['auto', 'auto']}
                    tick={{ fontSize: 11, fill: '#64748B' }}
                    tickFormatter={(v) => `$${(Number(v) / 1e9).toFixed(1)}B`}
                  />
                  <YAxis
                    yAxisId="right"
                    orientation="right"
                    domain={['auto', 'auto']}
                    tick={{ fontSize: 11, fill: '#10B981' }}
                    tickFormatter={(v) => `$${(Number(v) / 1e6).toFixed(0)}M`}
                  />
                  <Tooltip
                    formatter={(value: any, name: any) => {
                      const num = Number(value) || 0;
                      const abs = Math.abs(num);
                      const formatted = abs >= 1e9 ? `$${(num / 1e9).toFixed(2)}B` : `$${(num / 1e6).toFixed(1)}M`;
                      return [formatted, name];
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                  <Line yAxisId="left" type="monotone" dataKey="actualExpenditure" name="Actual Spend ($B)" stroke="#64748B" strokeWidth={2.5} dot={{ r: 4 }} />
                  <Line yAxisId="left" type="monotone" dataKey="benchmarkExpenditure" name="Benchmark Spend ($B)" stroke="#3B82F6" strokeWidth={2.5} strokeDasharray="4 4" dot={{ r: 4 }} />
                  <Line yAxisId="right" type="monotone" dataKey="savings" name="Gross Savings ($M)" stroke="#10B981" strokeWidth={2.5} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Contract Registry Section */}
      <div id="aco-table" className="bg-white rounded-xl border border-vbc-gray-light p-5 shadow-card mt-6 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-vbc-gray-light space-y-3 md:space-y-0">
          <div>
            <h3 className="font-bold text-base text-vbc-navy">MSSP ACO Contract Registry</h3>
            <p className="text-xs text-vbc-gray mt-0.5">Performance records for selected year {selectedYear}</p>
          </div>

          <div className="flex items-center space-x-3">
            {/* Year Selector */}
            <div className="flex items-center space-x-1.5">
              <span className="text-xs font-semibold text-vbc-gray">Performance Year:</span>
              <select
                value={selectedYear}
                onChange={(e) => {
                  setSelectedYear(Number(e.target.value));
                  setCurrentPage(1);
                }}
                className="bg-gray-50 border border-vbc-gray-light rounded-lg px-3 py-1.5 text-xs font-bold text-vbc-navy focus:outline-none focus:ring-2 focus:ring-vbc-blue"
              >
                {supportedYears.map((yr) => (
                  <option key={yr} value={yr}>
                    {yr}
                  </option>
                ))}
              </select>
            </div>

            {/* Risk level filter buttons */}
            <div className="flex items-center space-x-1 bg-gray-100 p-1 rounded-lg">
              {(['ALL', 'LOW', 'MEDIUM', 'HIGH'] as RiskFilter[]).map((level) => (
                <button
                  key={level}
                  onClick={() => {
                    setRiskFilter(level);
                    setCurrentPage(1);
                  }}
                  className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-colors ${
                    riskFilter === level
                      ? 'bg-white text-vbc-navy shadow-sm'
                      : 'text-vbc-gray hover:text-vbc-navy'
                  }`}
                >
                  {level === 'ALL' ? 'All' : level === 'LOW' ? 'Low Risk' : level === 'MEDIUM' ? 'Moderate' : 'High Risk'}
                </button>
              ))}
            </div>

            {/* Search input */}
            <div className="relative w-64">
              <Search size={14} className="absolute left-3 top-2.5 text-vbc-gray" />
              <input
                type="text"
                placeholder="Search ACO by name or ID..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full bg-gray-50 border border-vbc-gray-light hover:border-vbc-gray focus:border-vbc-blue focus:outline-none pl-9 pr-4 py-2 rounded-lg text-xs"
              />
            </div>
          </div>
        </div>

        {/* ACO Table list */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-vbc-gray-light text-xs font-bold text-vbc-gray uppercase tracking-wider bg-gray-50/50">
                <th className="p-3">ACO Panel Name</th>
                <th className="p-3">Risk Level</th>
                <th className="p-3">Attributed Members</th>
                <th className="p-3">Benchmark PMPM</th>
                <th className="p-3">Actual PMPM</th>
                <th className="p-3">Savings / (Loss)</th>
                <th className="p-3">Quality Score</th>
                <th className="p-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="text-xs divide-y divide-vbc-gray-light">
              {loading ? (
                <tr>
                  <td colSpan={8} className="text-center py-8 text-vbc-gray text-xs">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-vbc-blue mx-auto mb-2"></div>
                    Fetching Performance Year {selectedYear} ACO contracts...
                  </td>
                </tr>
              ) : pagedAcos.map((aco) => {
                const formattedSavings = new Intl.NumberFormat('en-US', {
                  style: 'currency',
                  currency: 'USD',
                  maximumFractionDigits: 0
                }).format(aco.savingsLoss);

                const isLoss = aco.savingsLoss < 0;

                return (
                  <tr key={aco.id} className="hover:bg-vbc-blue-light/35 transition-colors">
                    <td className="p-3 font-semibold text-vbc-navy">
                      <div>{aco.name}</div>
                      <span className="text-[10px] font-mono text-vbc-gray">{aco.id}</span>
                    </td>
                    <td className="p-3">
                      <StatusBadge type="risk" value={aco.riskLevel} />
                    </td>
                    <td className="p-3 font-medium text-vbc-navy">{aco.attributedMembers.toLocaleString()}</td>
                    <td className="p-3 text-vbc-gray">${aco.riskAdjustedBenchmarkPMPM.toFixed(2)}</td>
                    <td className="p-3 text-vbc-gray">${aco.actualPMPM.toFixed(2)}</td>
                    <td className={`p-3 font-bold ${isLoss ? 'text-vbc-red-dark' : 'text-vbc-green-dark'}`}>
                      {formattedSavings} ({aco.savingsLossPercent > 0 ? '+' : ''}
                      {aco.savingsLossPercent}%)
                    </td>
                    <td className="p-3 font-semibold text-vbc-navy">{aco.qualityScore}%</td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => navigate(`/aco/${aco.id}?year=${selectedYear}`)}
                        className="inline-flex items-center space-x-1 px-3 py-1.5 bg-vbc-blue hover:bg-vbc-blue-medium text-white text-xs font-semibold rounded-lg shadow-sm transition-colors"
                      >
                        <span>View</span>
                        <ChevronRight size={13} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {!loading && pagedAcos.length === 0 && (
            <div className="text-center py-8 text-vbc-gray text-xs">No contracts match the active filter parameters for Performance Year {selectedYear}.</div>
          )}
        </div>

        {/* Pagination controls */}
        {totalPages > 1 && (
          <div className="flex justify-between items-center text-xs text-vbc-navy pt-2 border-t border-vbc-gray-light">
            <button
              onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1.5 border border-vbc-gray-light rounded-lg hover:bg-gray-150 disabled:opacity-40"
            >
              Previous
            </button>
            <span className="font-semibold text-vbc-gray">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1.5 border border-vbc-gray-light rounded-lg hover:bg-gray-150 disabled:opacity-40"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
};
export default Dashboard;
