import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDataMode } from '../context/DataModeContext';
import { useACO, SUPPORTED_YEARS } from '../context/ACOContext';
import { usePageAIContext } from '../hooks/usePageAIContext';
import { Layout } from '../components/Layout';
import { StatusBadge } from '../components/StatusBadge';
import { peerTargetService } from '../services/peerTargetService';
import { forecastService } from '../services/forecastService';
import { PeerTargetProfile, SimilarPeer } from '../data/mock/peerTargetData';
import { ACOForecast } from '../data/mock/forecastData';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Target, Search, ArrowRight, TrendingUp, Lightbulb, CheckCircle, Loader2, ChevronRight } from 'lucide-react';

export const PeerTargetFinderPage: React.FC = () => {
  const navigate = useNavigate();
  const { dataMode } = useDataMode();
  const { availableAcos, selectedAcoId: globalSelectedAcoId, selectedYear, setSelectedYear } = useACO();
  const [selectedAcoId, setSelectedAcoId] = useState(globalSelectedAcoId || 'A1001');
  const [profile, setProfile] = useState<PeerTargetProfile | null>(null);
  const [forecast, setForecast] = useState<ACOForecast | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [peersOffset, setPeersOffset] = useState(0);
  const [allPeers, setAllPeers] = useState<SimilarPeer[]>([]);
  const [hasMore, setHasMore] = useState(false);
  const [totalPeers, setTotalPeers] = useState(0);

  useEffect(() => {
    if (availableAcos && availableAcos.length > 0) {
      const firstId = availableAcos[0].aco_id || availableAcos[0].id;
      if (firstId && (!selectedAcoId || selectedAcoId === 'lmn-aco')) {
        setSelectedAcoId(firstId);
      }
    }
  }, [availableAcos, selectedAcoId]);

  const runFind = async (acoId: string) => {
    setLoading(true);
    setPeersOffset(0);
    try {
      const effectiveId = acoId || (availableAcos[0]?.aco_id || availableAcos[0]?.id || 'A1001');
      const [peerRes, forecastRes] = await Promise.all([
        peerTargetService.getPeerTarget(effectiveId, dataMode, selectedYear, 20, 0),
        forecastService.getACOForecast(effectiveId, dataMode)
      ]);

      if (peerRes.success && peerRes.data) {
        setProfile(peerRes.data);
        setAllPeers(peerRes.data.similarPeers || []);
        setHasMore(peerRes.data.hasMore ?? false);
        setTotalPeers(peerRes.data.total ?? (peerRes.data.similarPeers?.length || 0));
        setPeersOffset(20);
      }
      if (forecastRes.success) setForecast(forecastRes.data);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadMore = async () => {
    if (loadingMore || !hasMore || !profile) return;
    setLoadingMore(true);
    try {
      const effectiveId = selectedAcoId || profile.acoId;
      const res = await peerTargetService.getPeerTarget(effectiveId, dataMode, selectedYear, 20, peersOffset);
      if (res.success && res.data && res.data.similarPeers) {
        setAllPeers((prev) => {
          const existingIds = new Set(prev.map((p) => p.acoId));
          const newUnique = res.data.similarPeers.filter((p) => !existingIds.has(p.acoId));
          return [...prev, ...newUnique];
        });
        setHasMore(res.data.hasMore ?? false);
        setPeersOffset((prev) => prev + 20);
      }
    } finally {
      setLoadingMore(false);
    }
  };

  useEffect(() => {
    const effectiveId = selectedAcoId || (availableAcos[0]?.aco_id || availableAcos[0]?.id || 'A1001');
    runFind(effectiveId);
  }, [dataMode, selectedAcoId, selectedYear]);

  usePageAIContext(
    {
      page: 'Peer Target Finder',
      route: '/peer-target-finder',
      acoId: profile?.acoId,
      acoName: profile?.acoName,
      year: selectedYear,
      currentSavings: profile?.currentSavingsRate,
      targetSavings: profile?.targetSavingsRate,
      currentQuality: profile?.currentQuality,
      targetQuality: profile?.targetQuality,
      currentPMPM: profile?.currentPMPM,
      targetPMPM: profile?.targetPMPM,
      similarPeers: allPeers.length
    },
    [profile?.acoId, selectedYear, allPeers.length]
  );

  const comparisonData = profile
    ? [
        { metric: 'Savings %', Current: profile.currentSavingsRate, Target: profile.targetSavingsRate },
        { metric: 'Quality %', Current: profile.currentQuality, Target: profile.targetQuality }
      ]
    : [];

  const pmpmData = profile ? [{ metric: 'PMPM $', Current: profile.currentPMPM, Target: profile.targetPMPM }] : [];

  return (
    <Layout title="Peer Target Finder" onLogout={() => {}}>
      {/* Test Status Banner */}
      <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3.5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 shadow-sm">
        <div className="flex items-center space-x-2 text-xs text-vbc-navy font-bold">
          <CheckCircle size={16} className="text-vbc-green-dark shrink-0" />
          <span>REAL-TIME DATABASE-DRIVEN PEER BENCHMARKING &amp; COHORT ANALYSIS</span>
        </div>
        <span className="text-[10px] uppercase font-bold text-vbc-green-dark bg-vbc-green-light px-2.5 py-1 rounded-md shrink-0">
          Connected to Supabase DB • PY {selectedYear} ({availableAcos.length} ACOs active)
        </span>
      </div>

      {/* Target ACO selector */}
      <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 space-y-4">
        <div className="flex items-center space-x-2 border-b border-vbc-gray-light pb-3">
          <Target size={16} className="text-vbc-blue" />
          <h3 className="font-bold text-sm text-vbc-navy">Target ACO Selection &amp; Peer Clustering</h3>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 items-end">
          <div className="flex-1 space-y-1 w-full">
            <span className="text-[10px] uppercase font-bold text-vbc-gray">Select Target ACO ({availableAcos.length} Available)</span>
            <select
              value={selectedAcoId}
              onChange={(e) => setSelectedAcoId(e.target.value)}
              className="w-full bg-gray-50 border border-vbc-gray-light rounded-lg px-3 py-2 text-xs font-semibold text-vbc-navy focus:outline-none focus:border-vbc-blue"
            >
              {availableAcos.map((a) => {
                const id = a.aco_id || a.id;
                const name = a.name || a.aco_name || id;
                return (
                  <option key={id} value={id}>
                    {name} ({id})
                  </option>
                );
              })}
            </select>
          </div>
          <div className="space-y-1">
            <span className="text-[10px] uppercase font-bold text-vbc-gray">Performance Year</span>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              className="bg-gray-50 border border-vbc-gray-light rounded-lg px-3 py-2 text-xs font-semibold text-vbc-navy focus:outline-none focus:border-vbc-blue cursor-pointer"
            >
              {SUPPORTED_YEARS.map((y) => (
                <option key={y} value={y}>
                  PY {y}
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={() => runFind(selectedAcoId)}
            className="flex items-center space-x-1.5 bg-vbc-blue hover:bg-vbc-blue-medium text-white px-4 py-2 rounded-lg text-xs font-semibold shadow-sm transition-colors"
          >
            <Search size={13} />
            <span>Find Target</span>
          </button>
        </div>
      </div>

      {loading || !profile ? (
        <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-10 text-center text-xs text-vbc-gray">
          <Loader2 size={24} className="animate-spin text-vbc-blue mx-auto mb-2" />
          Analyzing peer cohort for {selectedAcoId} (PY {selectedYear})...
        </div>
      ) : (
        <>
          {/* Current vs Classification */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-5 rounded-xl border border-vbc-gray-light shadow-card">
              <span className="text-[10px] uppercase font-bold text-vbc-gray">Current Savings</span>
              <div className={`text-2xl font-extrabold mt-1 ${profile.currentSavingsRate < 0 ? 'text-vbc-red-dark' : 'text-vbc-green-dark'}`}>
                {profile.currentSavingsRate > 0 ? '+' : ''}{profile.currentSavingsRate.toFixed(2)}%
              </div>
            </div>
            <div className="bg-white p-5 rounded-xl border border-vbc-gray-light shadow-card">
              <span className="text-[10px] uppercase font-bold text-vbc-gray">Current Quality</span>
              <div className="text-2xl font-extrabold mt-1 text-vbc-navy">{profile.currentQuality.toFixed(1)}%</div>
            </div>
            <div className="bg-white p-5 rounded-xl border border-vbc-gray-light shadow-card">
              <span className="text-[10px] uppercase font-bold text-vbc-gray">Current PMPM</span>
              <div className="text-2xl font-extrabold mt-1 text-vbc-navy">${profile.currentPMPM.toFixed(2)}</div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 flex items-center justify-between flex-wrap gap-3">
            <div>
              <span className="text-[10px] uppercase font-bold text-vbc-gray block">Performance Classification</span>
              <span className="font-bold text-vbc-navy text-sm">{profile.acoName}</span>
            </div>
            <StatusBadge
              type="status"
              value={
                profile.classification === 'Bottom Quartile' ? 'At Risk' : profile.classification === 'Mid Quartile' ? 'Needs Attention' : 'Good Standing'
              }
            />
          </div>

          {/* Peer Benchmark / Current vs Target */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 space-y-4">
              <h4 className="font-bold text-xs text-vbc-navy uppercase tracking-wider border-b border-vbc-gray-light pb-2">
                Current vs. Target — Savings &amp; Quality
              </h4>
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={comparisonData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F3F4F6" />
                    <XAxis dataKey="metric" tick={{ fill: '#6B7280', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: '#6B7280', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <Tooltip />
                    <Legend wrapperStyle={{ fontSize: 11 }} />
                    <Bar dataKey="Current" fill="#94A3B8" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="Target" fill="#2563EB" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 space-y-4">
              <h4 className="font-bold text-xs text-vbc-navy uppercase tracking-wider border-b border-vbc-gray-light pb-2">
                Current vs. Target — PMPM
              </h4>
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={pmpmData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F3F4F6" />
                    <XAxis dataKey="metric" tick={{ fill: '#6B7280', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: '#6B7280', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <Tooltip formatter={(v: any) => [`$${v}`, '']} />
                    <Legend wrapperStyle={{ fontSize: 11 }} />
                    <Bar dataKey="Current" fill="#94A3B8" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="Target" fill="#10B981" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Current -> Target quick view + gaps */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { label: 'Savings Gap', current: profile.currentSavingsRate, target: profile.targetSavingsRate, unit: '%' },
              { label: 'Quality Gap', current: profile.currentQuality, target: profile.targetQuality, unit: '%' },
              { label: 'PMPM Gap', current: profile.currentPMPM, target: profile.targetPMPM, unit: '$', invert: true }
            ].map((g, idx) => {
              const gap = g.invert ? g.current - g.target : g.target - g.current;
              return (
                <div key={idx} className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 space-y-2">
                  <span className="text-[10px] uppercase font-bold text-vbc-gray">{g.label}</span>
                  <div className="flex items-center space-x-2 text-xs font-semibold text-vbc-navy">
                    <span>{g.unit === '$' ? `$${g.current.toFixed(0)}` : `${g.current.toFixed(1)}%`}</span>
                    <ArrowRight size={12} className="text-vbc-gray" />
                    <span className="text-vbc-blue">{g.unit === '$' ? `$${g.target.toFixed(0)}` : `${g.target.toFixed(1)}%`}</span>
                  </div>
                  <div className={`text-lg font-extrabold ${gap >= 0 ? 'text-vbc-green-dark' : 'text-vbc-red-dark'}`}>
                    {gap >= 0 ? '+' : ''}{g.unit === '$' ? `$${gap.toFixed(0)}` : `${gap.toFixed(1)}pp`}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Forecast context (where relevant) */}
          {forecast && (
            <div className="grid grid-cols-1 gap-6">
              <div className="text-xs font-bold text-vbc-gray uppercase tracking-wider flex items-center gap-1.5">
                <TrendingUp size={13} /> Current → Forecast → Peer Target
              </div>
              <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5">
                <div className="grid grid-cols-3 text-center text-xs">
                  <div>
                    <span className="text-[9px] uppercase font-bold text-vbc-gray block">Current</span>
                    <span className="font-bold text-vbc-navy text-lg">{profile.currentSavingsRate.toFixed(2)}%</span>
                  </div>
                  <div>
                    <span className="text-[9px] uppercase font-bold text-vbc-gray block">{forecast.predictedYear} Forecast</span>
                    <span className="font-bold text-vbc-blue text-lg">{forecast.predictedSavingsRate.toFixed(2)}%</span>
                  </div>
                  <div>
                    <span className="text-[9px] uppercase font-bold text-vbc-gray block">Peer Target</span>
                    <span className="font-bold text-vbc-green-dark text-lg">{profile.targetSavingsRate.toFixed(2)}%</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Similar peers table */}
          <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 space-y-3">
            <div className="flex items-center justify-between border-b border-vbc-gray-light pb-2">
              <h4 className="font-bold text-xs text-vbc-navy uppercase tracking-wider">
                Similar Benchmark Peers ({allPeers.length} of {totalPeers || allPeers.length} Loaded)
              </h4>
              <span className="text-[10px] text-vbc-gray font-semibold">
                PY {selectedYear} Cohort
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-vbc-gray-light text-xs font-bold text-vbc-gray bg-gray-50/50">
                    <th className="p-3">Rank</th>
                    <th className="p-3">ACO ID</th>
                    <th className="p-3">ACO Name</th>
                    <th className="p-3">Similarity</th>
                    <th className="p-3">Savings %</th>
                    <th className="p-3">Quality Score</th>
                    <th className="p-3">PMPM</th>
                    <th className="p-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="text-xs divide-y divide-vbc-gray-light">
                  {allPeers.map((p) => (
                    <tr key={p.acoId} className="hover:bg-vbc-blue-light/35 transition-colors">
                      <td className="p-3 font-bold text-vbc-navy">#{p.rank}</td>
                      <td className="p-3 font-mono font-bold text-vbc-blue">{p.acoId}</td>
                      <td className="p-3 font-semibold text-vbc-navy">{p.acoName}</td>
                      <td className="p-3">
                        <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold bg-blue-50 text-vbc-blue border border-blue-200">
                          {p.similarityScore ? `${p.similarityScore.toFixed(1)}% Match` : 'Benchmark Peer'}
                        </span>
                      </td>
                      <td className={`p-3 font-bold ${(p.savingsRate ?? 0) < 0 ? 'text-vbc-red-dark' : 'text-vbc-green-dark'}`}>
                        {(p.savingsRate ?? 0) > 0 ? '+' : ''}{(p.savingsRate ?? 0).toFixed(2)}%
                      </td>
                      <td className="p-3 font-medium text-vbc-navy">{(p.qualityScore ?? 0).toFixed(1)}%</td>
                      <td className="p-3 font-medium text-vbc-navy">${(p.pmpm ?? 0).toFixed(2)}</td>
                      <td className="p-3 text-right">
                        <button
                          onClick={() => navigate(`/aco/${p.acoId}?year=${selectedYear}`)}
                          className="inline-flex items-center space-x-1 px-3 py-1 bg-vbc-blue hover:bg-vbc-blue-medium text-white text-[11px] font-semibold rounded-lg shadow-sm transition-colors cursor-pointer"
                        >
                          <span>View Details</span>
                          <ChevronRight size={12} />
                        </button>
                      </td>
                    </tr>
                  ))}
                  {allPeers.length === 0 && (
                    <tr>
                      <td colSpan={8} className="p-6 text-center text-xs text-vbc-gray">
                        No benchmark peers found for selected criteria.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Paginated Load More Control */}
            <div className="pt-3 border-t border-vbc-gray-light flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
              <span className="text-vbc-gray">
                Displaying <strong>{allPeers.length}</strong> of <strong>{totalPeers || allPeers.length}</strong> comparable ACOs
              </span>
              {hasMore ? (
                <button
                  onClick={handleLoadMore}
                  disabled={loadingMore}
                  className="inline-flex items-center space-x-2 px-4 py-2 bg-vbc-navy hover:bg-vbc-navy-dark text-white rounded-lg font-semibold text-xs transition-colors shadow-sm disabled:opacity-50"
                >
                  {loadingMore ? (
                    <>
                      <Loader2 size={14} className="animate-spin" />
                      <span>Loading More Peers...</span>
                    </>
                  ) : (
                    <span>Load More Peers</span>
                  )}
                </button>
              ) : (
                <span className="text-xs font-semibold text-vbc-gray bg-gray-100 px-3 py-1.5 rounded-lg">
                  All {allPeers.length} Peer Results Loaded
                </span>
              )}
            </div>
          </div>

          {/* Recommendation */}
          <div className="bg-vbc-blue-light/40 border border-vbc-blue/20 rounded-xl p-5 flex items-start space-x-3">
            <Lightbulb size={18} className="text-vbc-blue flex-shrink-0 mt-0.5" />
            <div>
              <span className="text-[10px] uppercase font-bold text-vbc-blue block">Recommendation</span>
              <p className="text-xs text-vbc-navy leading-relaxed mt-1">{profile.recommendation}</p>
            </div>
          </div>
        </>
      )}
    </Layout>
  );
};

export default PeerTargetFinderPage;

