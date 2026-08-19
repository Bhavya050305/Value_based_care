import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDataMode } from '../context/DataModeContext';
import { useACO } from '../context/ACOContext';
import { usePageAIContext } from '../hooks/usePageAIContext';
import { Layout } from '../components/Layout';
import { StatusBadge } from '../components/StatusBadge';
import { acoService } from '../services/acoService';
import { ACO } from '../types';
import { Search, ChevronRight, Compass } from 'lucide-react';

export const ACOExplorerPage: React.FC = () => {
  const navigate = useNavigate();
  const { dataMode } = useDataMode();
  const { selectedYear, setSelectedYear, supportedYears } = useACO();
  const [acos, setAcos] = useState<ACO[]>([]);
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAcos = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await acoService.getACOs(dataMode, selectedYear);
      if (res.success && res.data) {
        setAcos(res.data);
      } else {
        setAcos([]);
        setError(res.message || 'Unable to load ACO records for the selected performance year.');
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to connect to backend server.');
      setAcos([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAcos();
  }, [dataMode, selectedYear]);

  const filtered = acos.filter((aco) => {
    const matchesSearch = aco.name.toLowerCase().includes(search.toLowerCase()) || aco.id.toLowerCase().includes(search.toLowerCase());
    const matchesRisk = riskFilter === 'ALL' || aco.riskLevel === riskFilter;
    return matchesSearch && matchesRisk;
  });

  usePageAIContext({ page: 'ACO Explorer', route: '/explorer', year: selectedYear, visibleACOs: filtered.length }, [selectedYear, filtered.length]);

  return (
    <Layout title="ACO Explorer" onLogout={() => {}}>
      <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 space-y-5">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between border-b border-vbc-gray-light pb-4 space-y-3 lg:space-y-0">
          <div className="flex items-center space-x-2">
            <Compass size={20} className="text-vbc-blue" />
            <div>
              <h3 className="text-base font-bold text-vbc-navy">Search and Explore ACO Contracts</h3>
              <p className="text-xs text-vbc-gray mt-0.5">Discovered {acos.length} distinct ACOs for Performance Year {selectedYear}.</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 w-full lg:w-auto">
            <div className="flex items-center space-x-1.5">
              <span className="text-xs font-semibold text-vbc-gray">Performance Year:</span>
              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(Number(e.target.value))}
                className="bg-gray-50 border border-vbc-gray-light rounded-lg px-3 py-1.5 text-xs font-bold text-vbc-navy focus:outline-none focus:ring-2 focus:ring-vbc-blue"
              >
                {supportedYears.map((yr) => (
                  <option key={yr} value={yr}>
                    {yr}
                  </option>
                ))}
              </select>
            </div>

            <div className="relative flex-1 lg:w-72">
              <Search size={15} className="absolute left-3 top-2.5 text-vbc-gray" />
              <input
                type="text"
                placeholder="Search ACO by name or ID..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-gray-50 border border-vbc-gray-light hover:border-vbc-gray focus:border-vbc-blue focus:outline-none pl-9 pr-4 py-2 rounded-lg text-xs"
              />
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-[10px] uppercase font-bold text-vbc-gray">Risk Level Filter:</span>
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="bg-gray-50 border border-vbc-gray-light rounded-lg px-2.5 py-1.5 text-xs font-semibold text-vbc-navy focus:outline-none"
          >
            <option value="ALL">All Risk Levels ({acos.length})</option>
            <option value="LOW">Low Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="HIGH">High Risk</option>
          </select>
        </div>

        {loading ? (
          <div className="text-center py-12 text-vbc-gray text-xs">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-vbc-blue mx-auto mb-3"></div>
            Retrieving ACOs for Performance Year {selectedYear}...
          </div>
        ) : error ? (
          <div className="text-center py-12 bg-rose-50 border border-rose-200 rounded-xl p-6 space-y-3">
            <p className="text-xs font-bold text-rose-700">{error}</p>
            <button
              onClick={fetchAcos}
              className="px-4 py-2 bg-vbc-blue text-white rounded-lg text-xs font-bold shadow-sm hover:bg-vbc-blue-medium transition-colors"
            >
              Retry Loading ACOs
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((aco) => (
              <button
                key={aco.id}
                onClick={() => navigate(`/aco/${aco.id}?year=${selectedYear}`)}
                className="text-left bg-gray-50 hover:bg-vbc-blue-light/40 border border-vbc-gray-light rounded-xl p-4 transition-colors space-y-2 group"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] font-mono font-bold text-vbc-blue uppercase">{aco.id}</span>
                    <h4 className="font-bold text-sm text-vbc-navy leading-snug group-hover:text-vbc-blue transition-colors">{aco.name}</h4>
                  </div>
                  <StatusBadge type="risk" value={aco.riskLevel} />
                </div>
                <div className="text-xs text-vbc-gray space-y-1">
                  <div>Attributed Members: <span className="font-semibold text-vbc-navy">{(aco.attributedMembers ?? 0).toLocaleString()}</span></div>
                  <div>Quality Score: <span className="font-semibold text-vbc-navy">{aco.qualityScore ?? 0}%</span></div>
                </div>
                <div className="flex items-center justify-between pt-2 border-t border-vbc-gray-light/70">
                  <span className={`text-xs font-bold ${(aco.savingsLoss ?? 0) < 0 ? 'text-vbc-red-dark' : 'text-vbc-green-dark'}`}>
                    ${Math.abs(aco.savingsLoss ?? 0).toLocaleString(undefined, { maximumFractionDigits: 0 })} ({(aco.savingsLossPercent ?? 0) > 0 ? '+' : ''}{aco.savingsLossPercent ?? 0}%)
                  </span>
                  <span className="inline-flex items-center text-vbc-blue text-xs font-semibold group-hover:translate-x-1 transition-transform">
                    Explore <ChevronRight size={13} />
                  </span>
                </div>
              </button>
            ))}
            {filtered.length === 0 && (
              <div className="col-span-full text-center py-12 text-vbc-gray text-xs">
                No ACOs found for Performance Year {selectedYear} matching search criteria.
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default ACOExplorerPage;
