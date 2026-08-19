import React from 'react';
import { MemberRisk } from '../types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, Award } from 'lucide-react';

interface MemberRiskChartProps {
  memberRisk: MemberRisk;
}

export const MemberRiskChart: React.FC<MemberRiskChartProps> = ({ memberRisk }) => {
  const {
    totalAttributed,
    highRiskMembers,
    chronicMembers,
    disabledMembers,
    averageRiskScore,
    benchmarkWithoutAdjustment,
    benchmarkWithAdjustment,
    riskAdjustmentImpact,
    conditionPrevalence
  } = memberRisk;

  return (
    <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-6 space-y-6">
      <div className="border-b border-vbc-gray-light pb-4">
        <h3 className="text-lg font-bold text-vbc-navy">Member Attribution & Risk adjustment</h3>
        <p className="text-xs text-vbc-gray mt-0.5">
          Member profiles, chronic disease distributions, and benchmark adjustments derived from historical HCC coding.
        </p>
      </div>

      {/* Profile KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="p-4 bg-gray-50 rounded-lg border border-vbc-gray-light">
          <span className="text-[10px] uppercase font-bold text-vbc-gray">Attributed Members</span>
          <div className="text-lg font-bold text-vbc-navy mt-1">{totalAttributed.toLocaleString()}</div>
        </div>
        <div className="p-4 bg-vbc-red-light/30 border border-vbc-red/10 rounded-lg">
          <span className="text-[10px] uppercase font-bold text-vbc-red-dark">High-Risk Members</span>
          <div className="text-lg font-bold text-vbc-red-dark mt-1">{highRiskMembers.toLocaleString()}</div>
        </div>
        <div className="p-4 bg-vbc-orange-light/30 border border-vbc-orange/10 rounded-lg">
          <span className="text-[10px] uppercase font-bold text-vbc-orange-dark">Chronic Burden</span>
          <div className="text-lg font-bold text-vbc-orange-dark mt-1">{chronicMembers.toLocaleString()}</div>
        </div>
        <div className="p-4 bg-gray-50 rounded-lg border border-vbc-gray-light">
          <span className="text-[10px] uppercase font-bold text-vbc-gray">Disabled Members</span>
          <div className="text-lg font-bold text-vbc-navy mt-1">{disabledMembers.toLocaleString()}</div>
        </div>
        <div className="p-4 bg-indigo-50 border border-indigo-100 rounded-lg">
          <span className="text-[10px] uppercase font-bold text-indigo-700">Average Risk Score</span>
          <div className="text-lg font-bold text-indigo-700 mt-1">{averageRiskScore.toFixed(2)}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Condition Prevalence */}
        <div>
          <div className="flex items-center space-x-1.5 text-xs font-bold text-vbc-navy border-b border-vbc-gray-light pb-2 mb-4">
            <Activity size={14} className="text-vbc-gray" />
            <span>Condition Prevalence rates (%)</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={conditionPrevalence}
                layout="vertical"
                margin={{ top: 0, right: 10, left: 30, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#F3F4F6" />
                <XAxis type="number" unit="%" tick={{ fill: '#6B7280', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis dataKey="condition" type="category" tick={{ fill: '#0B1E36', fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #E5E7EB', borderRadius: '8px' }}
                  formatter={(value) => [`${value}%`, 'Prevalence']}
                />
                <Bar dataKey="rate" fill="#3B82F6" radius={[0, 4, 4, 0]} barSize={15} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Adjustment Impact */}
        <div className="border border-vbc-gray-light rounded-xl p-5 flex flex-col justify-between bg-vbc-blue-light/20">
          <div>
            <div className="flex items-center space-x-1.5 text-xs font-bold text-vbc-navy border-b border-vbc-gray-light pb-2 mb-4">
              <Award size={14} className="text-vbc-blue" />
              <span>HCC Coding Risk-Adjustment Impact</span>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between items-center bg-white p-3.5 rounded-lg border border-vbc-gray-light">
                <div>
                  <span className="text-xs font-semibold text-vbc-gray block">Base Benchmark (Unadjusted)</span>
                  <span className="text-sm font-semibold text-vbc-navy/60">Assuming average population risk</span>
                </div>
                <span className="text-lg font-bold text-vbc-navy/70">${benchmarkWithoutAdjustment.toFixed(2)} PMPM</span>
              </div>

              <div className="flex justify-between items-center bg-white p-3.5 rounded-lg border border-vbc-blue/20 shadow-sm">
                <div>
                  <span className="text-xs font-bold text-vbc-blue block">Risk-Adjusted Contract Benchmark</span>
                  <span className="text-sm font-semibold text-vbc-navy">Adjusted for chronic illness mix</span>
                </div>
                <span className="text-lg font-extrabold text-vbc-blue">${benchmarkWithAdjustment.toFixed(2)} PMPM</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-vbc-gray-light/60 flex items-center justify-between">
            <div>
              <span className="text-[10px] uppercase font-bold text-vbc-navy/60 block">Benchmark Premium Bump</span>
              <span className="text-xs text-vbc-gray block">Higher benchmark allows larger savings thresholds</span>
            </div>
            <div className="text-right">
              <div className="text-2xl font-extrabold text-vbc-green-dark">+{riskAdjustmentImpact.toFixed(2)}%</div>
              <span className="text-[10px] text-vbc-green font-bold">Positive HCC Coding Impact</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
export default MemberRiskChart;
