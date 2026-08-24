import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useDataMode } from '../context/DataModeContext';
import { useACO } from '../context/ACOContext';
import { usePageAIContext } from '../hooks/usePageAIContext';
import { Layout } from '../components/Layout';
import { MemberRiskChart } from '../components/MemberRiskChart';
import { acoService } from '../services/acoService';
import { memberService } from '../services/memberService';
import { ACO, MemberRisk } from '../types';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Compass, Users, Search } from 'lucide-react';

export const MemberAttributionPage: React.FC = () => {
  const { dataMode } = useDataMode();
  const { selectedAcoId, setSelectedAcoId, selectedYear, availableAcos } = useACO();
  const [searchParams] = useSearchParams();
  const [acos, setAcos] = useState<ACO[]>([]);
  const [acoId, setAcoId] = useState(searchParams.get('aco') || selectedAcoId || 'A1001');
  const [memberRisk, setMemberRisk] = useState<MemberRisk | null>(null);
  const [loading, setLoading] = useState(true);

  // Filters for member roster table
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRiskCategory, setSelectedRiskCategory] = useState<string>('ALL');

  useEffect(() => {
    if (selectedAcoId && selectedAcoId !== acoId) {
      setAcoId(selectedAcoId);
    }
  }, [selectedAcoId, acoId]);

  useEffect(() => {
    acoService.getACOs(dataMode).then((res) => {
      if (res.success) setAcos(res.data);
    });
  }, [dataMode]);

  useEffect(() => {
    setLoading(true);
    memberService.getMemberRisk(acoId, dataMode).then((res) => {
      if (res.success && res.data) {
        setMemberRisk(res.data);
      }
      setLoading(false);
    });
  }, [acoId, dataMode, selectedYear]);

  const handleAcoChange = (newAcoId: string) => {
    setAcoId(newAcoId);
    setSelectedAcoId(newAcoId);
  };

  const selectedAco = acos.find((a) => a.id === acoId || a.aco_id === acoId) || availableAcos.find((a) => a.aco_id === acoId || a.id === acoId);

  usePageAIContext(
    { page: 'Member Attribution', route: '/members', acoId, acoName: selectedAco?.name, memberData: memberRisk },
    [acoId, !!memberRisk]
  );

  // Filter members roster list
  const rawMembers = (memberRisk as any)?.membersList || [];
  const filteredMembers = rawMembers.filter((m: any) => {
    const matchesSearch = 
      m.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.memberId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.primaryCondition.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesRisk = 
      selectedRiskCategory === 'ALL' ||
      (selectedRiskCategory === 'HIGH' && m.riskCategory === 'High Risk') ||
      (selectedRiskCategory === 'MEDIUM' && m.riskCategory === 'Medium Risk') ||
      (selectedRiskCategory === 'LOW' && m.riskCategory === 'Low Risk');

    return matchesSearch && matchesRisk;
  });

  return (
    <Layout title="Member Attribution & Risk" acoId={acoId} acoName={selectedAco?.name} onLogout={() => {}}>
      {/* ACO Header Selector */}
      <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <Compass size={18} className="text-vbc-blue" />
          <div>
            <h3 className="font-bold text-sm text-vbc-navy">Attributed Member Population & Risk Distribution</h3>
            <p className="text-[11px] text-vbc-gray">Scoped to ACO: {selectedAco?.name || acoId} — Performance Year {selectedYear}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs text-vbc-gray font-semibold">Select ACO:</span>
          <select
            value={acoId}
            onChange={(e) => handleAcoChange(e.target.value)}
            className="bg-gray-50 border border-vbc-gray-light rounded-lg px-3 py-2 text-xs font-semibold text-vbc-navy focus:outline-none focus:ring-2 focus:ring-vbc-blue"
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
      </div>

      {loading || !memberRisk ? (
        <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-12 text-center text-xs text-vbc-gray">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-vbc-blue mx-auto mb-3"></div>
          Loading real-time member attribution data from Supabase...
        </div>
      ) : (
        <>
          {/* Top Population Risk Summary */}
          <MemberRiskChart memberRisk={memberRisk} />

          {/* Member Attribution Trends Over Time */}
          <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 space-y-4">
            <div className="border-b border-vbc-gray-light pb-2 flex items-center justify-between">
              <h4 className="font-bold text-xs text-vbc-navy uppercase tracking-wider">Member Attribution Trends Over Time</h4>
              <span className="text-[11px] text-vbc-gray font-medium">Historical & Current PY</span>
            </div>
            <div className="h-60">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={memberRisk.attributionTrend} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F3F4F6" />
                  <XAxis dataKey="year" tick={{ fill: '#6B7280', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: '#6B7280', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <Tooltip />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Line type="monotone" dataKey="total" name="Total Attributed" stroke="#2563EB" strokeWidth={2.5} />
                  <Line type="monotone" dataKey="highRisk" name="High Risk" stroke="#EF4444" strokeWidth={2} />
                  <Line type="monotone" dataKey="chronic" name="Chronic" stroke="#F97316" strokeWidth={2} />
                  <Line type="monotone" dataKey="disabled" name="Disabled" stroke="#6B7280" strokeWidth={1.5} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* REAL-TIME ATTRIBUTED BENEFICIARIES ROSTER TABLE */}
          <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-vbc-gray-light pb-4">
              <div className="flex items-center space-x-2">
                <Users size={18} className="text-vbc-blue" />
                <div>
                  <h4 className="font-bold text-sm text-vbc-navy">Attributed Beneficiary Roster</h4>
                  <p className="text-[11px] text-vbc-gray">Real-time CMS member attribution details & risk stratification</p>
                </div>
              </div>

              {/* Filters */}
              <div className="flex flex-wrap items-center gap-2">
                {/* Search */}
                <div className="relative">
                  <Search size={14} className="absolute left-2.5 top-2.5 text-vbc-gray" />
                  <input
                    type="text"
                    placeholder="Search member, ID, or condition..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-8 pr-3 py-1.5 bg-gray-50 border border-vbc-gray-light rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-vbc-blue w-56"
                  />
                </div>

                {/* Risk Filter Buttons */}
                <div className="flex items-center bg-gray-100 p-1 rounded-lg">
                  <button
                    onClick={() => setSelectedRiskCategory('ALL')}
                    className={`px-2.5 py-1 text-[11px] font-semibold rounded-md transition-all ${
                      selectedRiskCategory === 'ALL' ? 'bg-white text-vbc-navy shadow-sm' : 'text-vbc-gray hover:text-vbc-navy'
                    }`}
                  >
                    All ({rawMembers.length})
                  </button>
                  <button
                    onClick={() => setSelectedRiskCategory('HIGH')}
                    className={`px-2.5 py-1 text-[11px] font-semibold rounded-md transition-all ${
                      selectedRiskCategory === 'HIGH' ? 'bg-red-500 text-white shadow-sm' : 'text-red-600 hover:bg-red-50'
                    }`}
                  >
                    High Risk
                  </button>
                  <button
                    onClick={() => setSelectedRiskCategory('MEDIUM')}
                    className={`px-2.5 py-1 text-[11px] font-semibold rounded-md transition-all ${
                      selectedRiskCategory === 'MEDIUM' ? 'bg-amber-500 text-white shadow-sm' : 'text-amber-600 hover:bg-amber-50'
                    }`}
                  >
                    Medium
                  </button>
                  <button
                    onClick={() => setSelectedRiskCategory('LOW')}
                    className={`px-2.5 py-1 text-[11px] font-semibold rounded-md transition-all ${
                      selectedRiskCategory === 'LOW' ? 'bg-green-600 text-white shadow-sm' : 'text-green-600 hover:bg-green-50'
                    }`}
                  >
                    Low Risk
                  </button>
                </div>
              </div>
            </div>

            {/* Beneficiaries Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-gray-50 border-b border-vbc-gray-light text-[11px] font-bold text-vbc-gray uppercase">
                    <th className="py-2.5 px-3">Member ID</th>
                    <th className="py-2.5 px-3">Beneficiary Name</th>
                    <th className="py-2.5 px-3">Demographics</th>
                    <th className="py-2.5 px-3">Risk Score</th>
                    <th className="py-2.5 px-3">Risk Category</th>
                    <th className="py-2.5 px-3">Primary Condition</th>
                    <th className="py-2.5 px-3">Attribution Method</th>
                    <th className="py-2.5 px-3 text-right">PMPM Cost</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filteredMembers.length > 0 ? (
                    filteredMembers.map((m: any) => (
                      <tr key={m.id || m.memberId} className="hover:bg-gray-50/80 transition-colors">
                        <td className="py-2.5 px-3 font-mono text-[11px] font-semibold text-vbc-navy">{m.memberId}</td>
                        <td className="py-2.5 px-3 font-semibold text-vbc-navy">{m.name}</td>
                        <td className="py-2.5 px-3 text-vbc-gray">{m.age} yrs • {m.gender}</td>
                        <td className="py-2.5 px-3">
                          <span className={`font-mono font-bold ${
                            m.riskScore >= 2.0 ? 'text-red-600' : m.riskScore >= 1.1 ? 'text-amber-600' : 'text-green-600'
                          }`}>
                            {m.riskScore.toFixed(2)}
                          </span>
                        </td>
                        <td className="py-2.5 px-3">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                            m.riskCategory === 'High Risk'
                              ? 'bg-red-50 text-red-700 border border-red-200'
                              : m.riskCategory === 'Medium Risk'
                              ? 'bg-amber-50 text-amber-700 border border-amber-200'
                              : 'bg-green-50 text-green-700 border border-green-200'
                          }`}>
                            {m.riskCategory}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-vbc-navy font-medium">{m.primaryCondition}</td>
                        <td className="py-2.5 px-3 text-vbc-gray">{m.attributionType}</td>
                        <td className="py-2.5 px-3 text-right font-mono font-semibold text-vbc-navy">
                          ${m.pmpm.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={8} className="py-8 text-center text-vbc-gray text-xs">
                        No beneficiary records matching criteria.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </Layout>
  );
};

export default MemberAttributionPage;
