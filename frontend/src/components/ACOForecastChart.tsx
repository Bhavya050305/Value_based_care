import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ACOForecast } from '../data/mock/forecastData';
import { TrendingUp, TrendingDown, Minus, Gauge } from 'lucide-react';

interface ACOForecastChartProps {
  forecast: ACOForecast;
  title?: string;
  metricLabel?: string;
}

// Splits a single series into two overlapping datasets so Recharts can render
// the historical segment as a solid line and the predicted segment as a
// dashed line, while keeping one continuous visual line across the join year.
export const ACOForecastChart: React.FC<ACOForecastChartProps> = ({
  forecast,
  title = 'Historical Performance + Forecast',
  metricLabel = 'Savings Rate'
}) => {
  const series = forecast?.series || [];
  const chartData = series.map((pt) => ({
    year: pt.year,
    actual: pt.isPredicted ? null : pt.savingsRatePercent,
    predicted: pt.isPredicted ? pt.savingsRatePercent : null
  }));

  // Bridge the gap: carry the last actual point into the predicted series so the
  // dashed line visually connects to the solid line instead of floating separately.
  const lastActualIdx = [...chartData].reverse().findIndex((d) => d.actual !== null);
  if (lastActualIdx !== -1) {
    const idx = chartData.length - 1 - lastActualIdx;
    if (chartData[idx + 1]) {
      chartData[idx] = { ...chartData[idx], predicted: chartData[idx].actual };
    }
  }

  const rawTrend = forecast?.trend;
  const trendString = typeof rawTrend === 'object' && rawTrend !== null
    ? (rawTrend as any).direction || (rawTrend as any).trend_label || 'Stable'
    : String(rawTrend || 'Stable');

  const trendIcon =
    trendString.toLowerCase().includes('positive') || trendString.toLowerCase().includes('improving') ? (
      <TrendingUp size={14} className="text-vbc-green-dark" />
    ) : trendString.toLowerCase().includes('negative') || trendString.toLowerCase().includes('worsening') ? (
      <TrendingDown size={14} className="text-vbc-red-dark" />
    ) : (
      <Minus size={14} className="text-vbc-gray" />
    );

  return (
    <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 space-y-4">
      <div className="border-b border-vbc-gray-light pb-2 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div>
          <h4 className="font-bold text-xs text-vbc-navy uppercase tracking-wider">{title}</h4>
          <p className="text-[10px] text-vbc-gray mt-0.5">
            Solid = Actual ({series[0]?.year || 2021}–{forecast?.lastActualYear || 2023}) &nbsp;•&nbsp; Dashed = Predicted ({forecast?.predictedYear || 2024})
          </p>
        </div>
        <span
          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold border w-fit ${
            forecast?.forecastQuality === 'High'
              ? 'bg-vbc-green-light text-vbc-green-dark border-vbc-green/20'
              : forecast?.forecastQuality === 'Medium'
              ? 'bg-vbc-orange-light text-vbc-orange-dark border-vbc-orange/20'
              : 'bg-gray-100 text-vbc-gray border-vbc-gray-light'
          }`}
        >
          <Gauge size={11} />
          Forecast Quality: {forecast?.forecastQuality || 'Medium'}
        </span>
      </div>


      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F3F4F6" />
            <XAxis dataKey="year" tick={{ fill: '#6B7280', fontSize: 10 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: '#6B7280', fontSize: 10 }} axisLine={false} tickLine={false} unit="%" />
            <Tooltip formatter={(val: any) => [`${Number(val).toFixed(2)}%`, metricLabel]} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Line type="monotone" dataKey="actual" name="Actual" stroke="#2563EB" strokeWidth={2.5} dot={{ r: 3 }} connectNulls={false} />
            <Line
              type="monotone"
              dataKey="predicted"
              name="Predicted"
              stroke="#2563EB"
              strokeWidth={2.5}
              strokeDasharray="6 5"
              dot={{ r: 3 }}
              connectNulls
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2 border-t border-vbc-gray-light text-xs">
        <div>
          <span className="text-[9px] uppercase font-bold text-vbc-gray block">{forecast?.lastActualYear || 2023} Actual</span>
          <span className="font-bold text-vbc-navy">{(forecast?.lastActualSavingsRate ?? 0) > 0 ? '+' : ''}{(forecast?.lastActualSavingsRate ?? 0).toFixed(2)}%</span>
        </div>
        <div>
          <span className="text-[9px] uppercase font-bold text-vbc-gray block">{forecast?.predictedYear || 2024} Predicted</span>
          <span className="font-bold text-vbc-blue">{(forecast?.predictedSavingsRate ?? 0) > 0 ? '+' : ''}{(forecast?.predictedSavingsRate ?? 0).toFixed(2)}%</span>
        </div>
        <div>
          <span className="text-[9px] uppercase font-bold text-vbc-gray block">Expected Change</span>
          <span className="font-bold text-vbc-green-dark">+{(forecast?.expectedChangePp ?? 0).toFixed(2)} pp</span>
        </div>
        <div>
          <span className="text-[9px] uppercase font-bold text-vbc-gray block flex items-center gap-1">Trend</span>
          <span className="font-bold text-vbc-navy inline-flex items-center gap-1 capitalize">{trendIcon} {trendString}</span>
        </div>
      </div>
    </div>
  );
};

export default ACOForecastChart;
