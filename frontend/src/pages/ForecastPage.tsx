import React, { useState, useEffect, useCallback } from 'react';
import { useDataMode } from '../context/DataModeContext';
import { useACO } from '../context/ACOContext';
import { usePageAIContext } from '../hooks/usePageAIContext';
import { Layout } from '../components/Layout';
import { acoService } from '../services/acoService';
import { forecastService } from '../services/forecastService';
import { ACO } from '../types';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  DollarSign, 
  Calendar, 
  Sparkles,
  ShieldCheck,
  Info
} from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine
} from 'recharts';

export const ForecastPage: React.FC = () => {
  const { dataMode } = useDataMode();
  const { selectedAcoId, availableAcos } = useACO();
  const [acos, setAcos] = useState<ACO[]>([]);
  const [targetAcoId, setTargetAcoId] = useState(selectedAcoId || 'A1001');
  const [forecastData, setForecastData] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedAcoId) {
      setTargetAcoId(selectedAcoId);
    }
  }, [selectedAcoId]);

  useEffect(() => {
    acoService.getACOs(dataMode).then((res) => {
      if (res.success) setAcos(res.data);
    });
  }, [dataMode]);

  const loadForecast = useCallback(async (acoIdToFetch: string) => {
    setLoading(true);
    try {
      const res = await forecastService.getACOForecast(acoIdToFetch, dataMode);
      if (res.success && res.data) {
        setForecastData(res.data);
      }
    } catch (err) {
      console.error('Error fetching 3-year forecast:', err);
    } finally {
      setLoading(false);
    }
  }, [dataMode]);

  // Load 3-year financial forecast whenever target ACO changes
  useEffect(() => {
    if (targetAcoId) {
      loadForecast(targetAcoId);
    }
  }, [targetAcoId, loadForecast]);

  const selectedAco =
    availableAcos.find((a) => a.aco_id === targetAcoId || a.id === targetAcoId) ||
    acos.find((a) => a.id === targetAcoId || a.aco_id === targetAcoId);

  const acoDisplayName = forecastData?.aco_name || selectedAco?.name || targetAcoId;

  usePageAIContext(
    {
      page: 'ACO Financial Trend Forecast',
      route: '/forecast',
      acoId: targetAcoId,
      acoName: acoDisplayName,
      forecast: forecastData
    },
    [targetAcoId, forecastData?.aco_id]
  );

  // Format currency helpers
  const formatCurrency = (val: number | null | undefined) => {
    if (val === null || val === undefined) return '$0';
    return `$${val.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
  };

  const formatPmpm = (val: number | null | undefined) => {
    if (val === null || val === undefined) return '$0.00';
    return `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const formatPct = (val: number | null | undefined) => {
    if (val === null || val === undefined) return '—';
    const sign = val > 0 ? '+' : '';
    return `${sign}${val.toFixed(1)}%`;
  };

  // Prepare chart data series (bridging 2024 to 2025 seamlessly)
  const combinedSeries = forecastData?.combined_series || [];
  const chartData = combinedSeries.map((item: any) => ({
    year: String(item.year),
    actualExp: item.status === 'actual' ? item.expenditure : null,
    forecastExp: item.status === 'forecast' || item.year === 2024 ? item.expenditure : null,
    benchmark: item.benchmark,
    status: item.status,
    pmpm: item.pmpm,
    benchmarkPmpm: item.benchmark_pmpm,
    savingsLoss: item.savings_loss
  }));

  const trend = forecastData?.trend || {};
  const summary = forecastData?.summary || {};

  const trendDirection = trend.direction || 'stable';
  const trendLabel = trend.trend_label || 'Stable';
  const change2027 = trend.change_2024_to_2027 || 0;

  return (
    <Layout
      title="ACO Financial Trend Forecast"
      acoId={targetAcoId}
      acoName={acoDisplayName}
      onLogout={() => {}}
    >
      <div className="space-y-6">
        {/* Top Context & ACO Selector Bar */}
        <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-vbc-gray-light pb-3">
            <div>
              <div className="flex items-center space-x-2">
                <TrendingUp size={20} className="text-vbc-blue" />
                <h3 className="font-bold text-base text-vbc-navy">ACO Financial Trend Forecast</h3>
              </div>
              <p className="text-xs text-vbc-gray mt-1">
                Historical performance (2022–2024) with projected 3-year financial outlook (2025–2027)
              </p>
            </div>

            <div className="flex items-center space-x-2 bg-blue-50 border border-blue-200 text-blue-800 px-3 py-1.5 rounded-lg text-xs font-semibold">
              <ShieldCheck size={14} className="text-vbc-blue" />
              <span>Connected Mode Active — Scoped strictly to {targetAcoId}</span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 items-end justify-between">
            <div className="flex-1 space-y-1 w-full max-w-md">
              <label className="text-[10px] uppercase font-bold text-vbc-gray block">Select ACO Network</label>
              <select
                value={targetAcoId}
                onChange={(e) => setTargetAcoId(e.target.value)}
                className="w-full bg-gray-50 border border-vbc-gray-light rounded-lg px-3.5 py-2 text-xs font-semibold text-vbc-navy focus:outline-none focus:ring-2 focus:ring-vbc-blue transition-all"
              >
                {availableAcos.length > 0 ? (
                  availableAcos.map((a) => (
                    <option key={a.aco_id || a.id} value={a.aco_id || a.id}>
                      {a.name} ({a.aco_id})
                    </option>
                  ))
                ) : (
                  acos.map((a) => (
                    <option key={a.id} value={a.id}>{a.name}</option>
                  ))
                )}
              </select>
            </div>

            <div className="flex items-center space-x-4 text-xs font-semibold text-vbc-navy bg-gray-50 px-4 py-2 rounded-lg border border-vbc-gray-light">
              <div>
                <span className="text-[10px] uppercase font-bold text-vbc-gray block">Historical Baseline</span>
                <span className="text-vbc-blue font-bold">2022 – 2024 (Actual)</span>
              </div>
              <div className="h-6 w-px bg-vbc-gray-light"></div>
              <div>
                <span className="text-[10px] uppercase font-bold text-vbc-gray block">Forecast Horizon</span>
                <span className="text-purple-600 font-bold">2025 – 2027 (Forecast)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Loading Indicator */}
        {loading && (
          <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-12 text-center text-xs text-vbc-gray">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-vbc-blue mx-auto mb-3"></div>
            Calculating 3-year ACO financial trajectory and risk-adjusted expenditure projections for {targetAcoId}...
          </div>
        )}

        {/* Dynamic Forecast Content */}
        {!loading && forecastData && (
          <>
            {/* Top 4 Business KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Card 1: 2025 Projected Expenditure */}
              <div className="bg-white rounded-xl border border-vbc-gray-light p-4 shadow-card hover:shadow-card-hover transition-all">
                <span className="text-[10px] font-bold text-vbc-gray uppercase tracking-wider block">
                  2025 Projected Expenditure
                </span>
                <div className="text-xl font-bold font-mono text-vbc-navy mt-1">
                  {formatCurrency(trend.projected_expenditure_2025)}
                </div>
                <div className="mt-2 flex items-center justify-between text-xs">
                  <span className="text-vbc-gray">vs 2024 Actual</span>
                  <span className={`font-bold ${trend.yoy_2025 <= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                    {formatPct(trend.yoy_2025)}
                  </span>
                </div>
              </div>

              {/* Card 2: 2026 Projected Expenditure */}
              <div className="bg-white rounded-xl border border-vbc-gray-light p-4 shadow-card hover:shadow-card-hover transition-all">
                <span className="text-[10px] font-bold text-vbc-gray uppercase tracking-wider block">
                  2026 Projected Expenditure
                </span>
                <div className="text-xl font-bold font-mono text-vbc-navy mt-1">
                  {formatCurrency(trend.projected_expenditure_2026)}
                </div>
                <div className="mt-2 flex items-center justify-between text-xs">
                  <span className="text-vbc-gray">vs 2025 Projected</span>
                  <span className={`font-bold ${trend.yoy_2026 <= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                    {formatPct(trend.yoy_2026)}
                  </span>
                </div>
              </div>

              {/* Card 3: 2027 Projected Expenditure */}
              <div className="bg-white rounded-xl border border-vbc-gray-light p-4 shadow-card hover:shadow-card-hover transition-all">
                <span className="text-[10px] font-bold text-vbc-gray uppercase tracking-wider block">
                  2027 Projected Expenditure
                </span>
                <div className="text-xl font-bold font-mono text-vbc-navy mt-1">
                  {formatCurrency(trend.projected_expenditure_2027)}
                </div>
                <div className="mt-2 flex items-center justify-between text-xs">
                  <span className="text-vbc-gray">vs 2026 Projected</span>
                  <span className={`font-bold ${trend.yoy_2027 <= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                    {formatPct(trend.yoy_2027)}
                  </span>
                </div>
              </div>

              {/* Card 4: 3-Year Forecast Trend */}
              <div className="bg-white rounded-xl border border-vbc-gray-light p-4 shadow-card hover:shadow-card-hover transition-all">
                <span className="text-[10px] font-bold text-vbc-gray uppercase tracking-wider block">
                  3-Year Forecast Trend
                </span>
                <div className="flex items-center space-x-2 mt-1">
                  <span className={`text-xl font-bold font-mono ${trendDirection === 'improving' ? 'text-emerald-600' : (trendDirection === 'worsening' ? 'text-rose-600' : 'text-vbc-navy')}`}>
                    {formatPct(change2027)}
                  </span>
                  {trendDirection === 'improving' ? (
                    <TrendingDown className="text-emerald-600" size={20} />
                  ) : trendDirection === 'worsening' ? (
                    <TrendingUp className="text-rose-600" size={20} />
                  ) : (
                    <Minus className="text-vbc-gray" size={20} />
                  )}
                </div>
                <div className="mt-2 flex items-center justify-between text-xs">
                  <span className="text-vbc-gray">Outlook Trajectory</span>
                  <span className={`font-bold uppercase text-[11px] px-2 py-0.5 rounded ${
                    trendDirection === 'improving' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                    trendDirection === 'worsening' ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                    'bg-gray-100 text-vbc-navy border border-gray-200'
                  }`}>
                    {trendLabel}
                  </span>
                </div>
              </div>
            </div>

            {/* Projected Gross Savings / Loss Breakdown */}
            <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 space-y-3">
              <div className="flex items-center space-x-2 border-b border-vbc-gray-light pb-2.5">
                <DollarSign size={18} className="text-emerald-600" />
                <h4 className="font-bold text-xs text-vbc-navy uppercase tracking-wider">
                  Projected Savings / Loss Outlook (2025–2027)
                </h4>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-gray-50 border border-vbc-gray-light rounded-lg p-3.5 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] font-bold text-vbc-gray uppercase">2025 Projected Savings</span>
                    <div className={`text-base font-bold font-mono mt-0.5 ${(trend.projected_savings_2025 || 0) >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                      {formatCurrency(trend.projected_savings_2025)}
                    </div>
                  </div>
                  <span className="text-xs font-semibold text-vbc-gray">PY 2025</span>
                </div>

                <div className="bg-gray-50 border border-vbc-gray-light rounded-lg p-3.5 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] font-bold text-vbc-gray uppercase">2026 Projected Savings</span>
                    <div className={`text-base font-bold font-mono mt-0.5 ${(trend.projected_savings_2026 || 0) >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                      {formatCurrency(trend.projected_savings_2026)}
                    </div>
                  </div>
                  <span className="text-xs font-semibold text-vbc-gray">PY 2026</span>
                </div>

                <div className="bg-gray-50 border border-vbc-gray-light rounded-lg p-3.5 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] font-bold text-vbc-gray uppercase">2027 Projected Savings</span>
                    <div className={`text-base font-bold font-mono mt-0.5 ${(trend.projected_savings_2027 || 0) >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                      {formatCurrency(trend.projected_savings_2027)}
                    </div>
                  </div>
                  <span className="text-xs font-semibold text-vbc-gray">PY 2027</span>
                </div>
              </div>
            </div>

            {/* Main Interactive Chart: ACO Financial Performance Trend & 3-Year Forecast */}
            <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-vbc-gray-light pb-3 gap-2">
                <div>
                  <h4 className="font-bold text-sm text-vbc-navy uppercase tracking-wider">
                    ACO Financial Performance Trend & 3-Year Forecast
                  </h4>
                  <p className="text-[11px] text-vbc-gray mt-0.5">
                    Actual performance: 2022–2024 &nbsp;|&nbsp; Forecast: 2025–2027
                  </p>
                </div>

                <div className="flex items-center space-x-4 text-[11px] font-semibold">
                  <span className="flex items-center space-x-1.5">
                    <span className="w-3 h-3 rounded-full bg-vbc-blue inline-block"></span>
                    <span className="text-vbc-navy">Actual Expenditure</span>
                  </span>
                  <span className="flex items-center space-x-1.5">
                    <span className="w-3 h-3 rounded-full bg-purple-600 inline-block"></span>
                    <span className="text-vbc-navy">Forecast Expenditure</span>
                  </span>
                  <span className="flex items-center space-x-1.5">
                    <span className="w-3 h-0.5 bg-amber-500 inline-block"></span>
                    <span className="text-vbc-navy">Benchmark Target</span>
                  </span>
                </div>
              </div>

              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={chartData} margin={{ top: 15, right: 20, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                    <XAxis dataKey="year" tick={{ fill: '#4B5563', fontSize: 11, fontWeight: 600 }} axisLine={false} tickLine={false} />
                    <YAxis
                      tick={{ fill: '#4B5563', fontSize: 11 }}
                      axisLine={false}
                      tickLine={false}
                      tickFormatter={(val) => `$${(val / 1000000).toFixed(0)}M`}
                    />
                    <Tooltip
                      formatter={(val: any, name: string) => [
                        formatCurrency(Number(val)),
                        name === 'actualExp' ? 'Actual Expenditure' : name === 'forecastExp' ? 'Forecast Expenditure' : 'Benchmark Target'
                      ]}
                      contentStyle={{ backgroundColor: '#FFFFFF', borderRadius: '8px', border: '1px solid #E5E7EB', fontSize: '12px' }}
                    />
                    <ReferenceLine x="2024" stroke="#9CA3AF" strokeDasharray="3 3" label={{ value: 'Forecast Horizon →', position: 'top', fill: '#6B7280', fontSize: 10, fontWeight: 700 }} />
                    <Line
                      type="monotone"
                      dataKey="actualExp"
                      name="Actual Expenditure"
                      stroke="#2563EB"
                      strokeWidth={3}
                      dot={{ r: 5, fill: '#2563EB', strokeWidth: 2, stroke: '#FFFFFF' }}
                      connectNulls={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="forecastExp"
                      name="Forecast Expenditure"
                      stroke="#9333EA"
                      strokeWidth={3}
                      strokeDasharray="6 6"
                      dot={{ r: 5, fill: '#9333EA', strokeWidth: 2, stroke: '#FFFFFF' }}
                      connectNulls
                    />
                    <Line
                      type="monotone"
                      dataKey="benchmark"
                      name="Benchmark Target"
                      stroke="#F59E0B"
                      strokeWidth={2}
                      dot={{ r: 3, fill: '#F59E0B' }}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Year-by-Year Forecast Table */}
            <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 space-y-4">
              <div className="flex items-center space-x-2 border-b border-vbc-gray-light pb-3">
                <Calendar size={18} className="text-vbc-blue" />
                <h4 className="font-bold text-xs text-vbc-navy uppercase tracking-wider">
                  Year-by-Year Financial Performance & Forecast Table
                </h4>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-gray-50 border-b border-vbc-gray-light text-[11px] font-bold text-vbc-gray uppercase">
                      <th className="py-3 px-4">Performance Year</th>
                      <th className="py-3 px-4">Status</th>
                      <th className="py-3 px-4 text-right">Actual / Projected Expenditure</th>
                      <th className="py-3 px-4 text-right">Benchmark Target</th>
                      <th className="py-3 px-4 text-right">Gross Savings / Loss</th>
                      <th className="py-3 px-4 text-right">PMPM Spending</th>
                      <th className="py-3 px-4 text-right">YoY Change (%)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {combinedSeries.map((row: any) => (
                      <tr
                        key={row.year}
                        className={`transition-colors ${
                          row.status === 'forecast' ? 'bg-purple-50/30 hover:bg-purple-50/60 font-semibold' : 'hover:bg-gray-50'
                        }`}
                      >
                        <td className="py-3 px-4 font-bold text-vbc-navy">
                          {row.year}
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                              row.status === 'actual'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-purple-100 text-purple-800'
                            }`}
                          >
                            {row.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right font-mono font-bold text-vbc-navy">
                          {formatCurrency(row.expenditure)}
                        </td>
                        <td className="py-3 px-4 text-right font-mono text-vbc-gray">
                          {formatCurrency(row.benchmark)}
                        </td>
                        <td className={`py-3 px-4 text-right font-mono font-bold ${row.savings_loss >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                          {formatCurrency(row.savings_loss)}
                        </td>
                        <td className="py-3 px-4 text-right font-mono text-vbc-navy">
                          {formatPmpm(row.pmpm)}
                        </td>
                        <td className={`py-3 px-4 text-right font-mono font-bold ${
                          row.yoy_change === null ? 'text-vbc-gray' : (row.yoy_change <= 0 ? 'text-emerald-600' : 'text-rose-600')
                        }`}>
                          {formatPct(row.yoy_change)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Forecast Outlook / Executive Narrative Section */}
            <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 space-y-3">
              <div className="flex items-center space-x-2 border-b border-vbc-gray-light pb-2.5">
                <Sparkles size={18} className="text-vbc-blue" />
                <h4 className="font-bold text-xs text-vbc-navy uppercase tracking-wider">
                  Executive Forecast Outlook
                </h4>
              </div>

              <div className="p-4 bg-gray-50 border border-vbc-gray-light rounded-lg text-xs leading-relaxed text-vbc-navy space-y-2">
                <p className="font-medium">
                  {summary.narrative || 'Forecast calculations updated based on real historical data.'}
                </p>
                <div className="flex items-center space-x-2 text-[11px] text-vbc-gray pt-1 border-t border-gray-200">
                  <Info size={13} className="text-vbc-blue" />
                  <span>
                    Baseline data derived from verified database tables (2022–2024) and projected across 2025–2027 using ACO-specific financial trajectory parameters.
                  </span>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
};

export default ForecastPage;
