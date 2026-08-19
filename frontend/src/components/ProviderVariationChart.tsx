import React from 'react';
import { Provider } from '../types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { AlertCircle, Users } from 'lucide-react';

interface ProviderVariationChartProps {
  providers: Provider[];
}

export const ProviderVariationChart: React.FC<ProviderVariationChartProps> = ({ providers }) => {
  // Aggregate stats
  const avgActual = providers.reduce((acc, curr) => acc + curr.actualPMPM, 0) / (providers.length || 1);
  const avgPeer = providers.reduce((acc, curr) => acc + curr.peerPMPM, 0) / (providers.length || 1);
  const highestVar = Math.max(...providers.map(p => p.variance));
  const highVarCount = providers.filter(p => p.variance > 15).length;

  const chartData = providers.map(p => ({
    name: p.name.split(' ').slice(1).join(' ') || p.name, // Just show last name
    PMPM: p.actualPMPM,
    Peer: p.peerPMPM,
    Variance: p.variance
  }));

  return (
    <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-6 space-y-6">
      <div className="border-b border-vbc-gray-light pb-4">
        <h3 className="text-lg font-bold text-vbc-navy">Provider Cost Variation</h3>
        <p className="text-xs text-vbc-gray mt-0.5">
          Provider variation identifies providers whose cost/utilization patterns differ significantly from peers.
        </p>
      </div>

      {/* Aggregate KPI grids */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 bg-gray-50 rounded-lg border border-vbc-gray-light">
          <span className="text-[10px] uppercase font-bold text-vbc-gray">Average Provider PMPM</span>
          <div className="text-lg font-bold text-vbc-navy mt-1">${avgActual.toFixed(0)}</div>
        </div>
        <div className="p-4 bg-gray-50 rounded-lg border border-vbc-gray-light">
          <span className="text-[10px] uppercase font-bold text-vbc-gray">Peer Benchmark PMPM</span>
          <div className="text-lg font-bold text-vbc-gray mt-1">${avgPeer.toFixed(0)}</div>
        </div>
        <div className="p-4 bg-vbc-red-light/50 border border-vbc-red/20 rounded-lg">
          <span className="text-[10px] uppercase font-bold text-vbc-red-dark">Highest Cost Variation</span>
          <div className="text-lg font-extrabold text-vbc-red-dark mt-1">+{highestVar.toFixed(1)}%</div>
        </div>
        <div className="p-4 bg-vbc-orange-light/50 border border-vbc-orange/20 rounded-lg">
          <span className="text-[10px] uppercase font-bold text-vbc-orange-dark font-medium">Outlier Providers (&gt;15%)</span>
          <div className="text-lg font-extrabold text-vbc-orange-dark mt-1">{highVarCount}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recharts chart */}
        <div className="lg:col-span-2 h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F3F4F6" />
              <XAxis dataKey="name" tick={{ fill: '#6B7280', fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#6B7280', fontSize: 10 }} axisLine={false} tickLine={false} unit="$" />
              <Tooltip
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #E5E7EB', borderRadius: '8px' }}
                labelStyle={{ fontWeight: 'bold', color: '#0B1E36' }}
              />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="PMPM" name="Actual Provider PMPM" fill="#2563EB" radius={[4, 4, 0, 0]} barSize={25} />
              <Bar dataKey="Peer" name="Peer Benchmark PMPM" fill="#94A3B8" radius={[4, 4, 0, 0]} barSize={25} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* List of providers */}
        <div className="border border-vbc-gray-light rounded-xl p-4 overflow-hidden flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-1.5 text-xs font-bold text-vbc-navy border-b border-vbc-gray-light pb-2 mb-3">
              <Users size={14} className="text-vbc-gray" />
              <span>Provider Panel Metrics</span>
            </div>

            <div className="space-y-3 max-h-48 overflow-y-auto pr-1">
              {providers.map((p, idx) => {
                const isHigh = p.variance > 15;
                return (
                  <div key={idx} className="flex justify-between items-center text-xs border-b border-gray-50 pb-2">
                    <div>
                      <div className="font-semibold text-vbc-navy">{p.name}</div>
                      <div className="text-[10px] text-vbc-gray">{p.specialty} • {p.attributedMembers} members</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-vbc-navy">${p.actualPMPM}</div>
                      <div className={`text-[10px] font-bold ${isHigh ? 'text-vbc-red-dark' : 'text-vbc-green-dark'}`}>
                        {p.variance > 0 ? '+' : ''}{p.variance.toFixed(1)}% vs peer
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {highVarCount > 0 && (
            <div className="mt-4 p-3 bg-vbc-red-light border border-vbc-red/10 rounded-lg flex items-start space-x-2 text-[11px] text-vbc-red-dark">
              <AlertCircle size={14} className="flex-shrink-0 mt-0.5" />
              <span>
                <strong>Action Needed:</strong> Outlier PMPM variance detected. Audit clinician claims codes and standardize cardiology/specialty referrals.
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
export default ProviderVariationChart;
