import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePageAIContext } from '../hooks/usePageAIContext';
import { Layout } from '../components/Layout';
import { useACO, SUPPORTED_YEARS } from '../context/ACOContext';
import { useDataMode } from '../context/DataModeContext';
import { alertService } from '../services/alertService';
import { Alert, AnomalyAlertsCounts } from '../types';
import {
  BellRing,
  ChevronRight,
  Search,
  Filter,
  AlertTriangle,
  Calendar,
  ChevronLeft
} from 'lucide-react';

const PAGE_SIZE = 20;

export const AlertsPage: React.FC = () => {
  const navigate = useNavigate();
  const { selectedYear, setSelectedYear } = useACO();
  const { dataMode } = useDataMode();

  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [counts, setCounts] = useState<AnomalyAlertsCounts>({
    total: 0,
    high: 0,
    medium: 0,
    low: 0,
    normal: 0,
  });
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<number>(1);

  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    try {
      const res = await alertService.getAlerts(selectedYear, dataMode);
      if (res.success && res.data) {
        setAlerts(res.data.alerts);
        setCounts(res.data.counts);
      }
    } catch (err) {
      console.error('Error loading portfolio anomaly alerts:', err);
    } finally {
      setLoading(false);
    }
  }, [selectedYear, dataMode]);

  useEffect(() => {
    fetchAlerts();
    setCurrentPage(1);
  }, [fetchAlerts]);

  const handleResolve = (id: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: 'reviewed' as const } : a))
    );
  };

  // Filtered dataset logic
  const filtered = alerts.filter((a) => {
    const matchesSeverity = severityFilter === 'ALL' || a.severity === severityFilter;
    const matchesSearch =
      searchQuery.trim() === '' ||
      a.aco.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.acoId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.metric.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSeverity && matchesSearch;
  });

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE) || 1;
  const pageStart = (currentPage - 1) * PAGE_SIZE;
  const paginatedAlerts = filtered.slice(pageStart, pageStart + PAGE_SIZE);

  usePageAIContext(
    {
      page: 'Alerts & Attention',
      route: '/alerts',
      year: selectedYear,
      totalEvaluated: counts.total,
      highSeverityCount: counts.high,
      mediumSeverityCount: counts.medium,
      alerts: filtered.slice(0, 10),
    },
    [selectedYear, counts.total, severityFilter, searchQuery]
  );

  return (
    <Layout title="Alerts & Attention — ML Anomaly Detection" onLogout={() => {}}>
      {/* Top Banner & Filters */}
      <div className="space-y-4">
        <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-vbc-red-light rounded-xl">
              <BellRing size={20} className="text-vbc-red" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-vbc-navy">
                Portfolio Anomaly & Risk Detection
              </h3>
              <p className="text-[11px] text-vbc-gray mt-0.5">
                LOF Model predictions across all {counts.total} ACOs for PY {selectedYear} • {counts.high} High & {counts.medium} Medium anomalies
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Year Selector */}
            <div className="flex items-center space-x-1.5 bg-gray-50 border border-vbc-gray-light px-3 py-1.5 rounded-lg text-xs">
              <Calendar size={13} className="text-vbc-gray" />
              <span className="text-[10px] font-bold uppercase text-vbc-gray">Year:</span>
              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(Number(e.target.value))}
                className="bg-transparent font-bold text-vbc-navy focus:outline-none cursor-pointer"
              >
                {SUPPORTED_YEARS.map((y) => (
                  <option key={y} value={y}>
                    PY {y}
                  </option>
                ))}
              </select>
            </div>

            {/* Severity Dropdown */}
            <div className="flex items-center space-x-1.5 bg-gray-50 border border-vbc-gray-light px-3 py-1.5 rounded-lg text-xs">
              <Filter size={13} className="text-vbc-gray" />
              <select
                value={severityFilter}
                onChange={(e) => {
                  setSeverityFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="bg-transparent font-bold text-vbc-navy focus:outline-none cursor-pointer"
              >
                <option value="ALL">All Severities ({counts.total})</option>
                <option value="HIGH">High Severity ({counts.high})</option>
                <option value="MEDIUM">Medium Severity ({counts.medium})</option>
                <option value="LOW">Low Severity ({counts.low})</option>
                <option value="NORMAL">Normal ({counts.normal})</option>
              </select>
            </div>
          </div>
        </div>

        {/* Dynamic Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <button
            onClick={() => { setSeverityFilter('ALL'); setCurrentPage(1); }}
            className={`p-3.5 rounded-xl border text-left transition-all ${
              severityFilter === 'ALL'
                ? 'bg-vbc-navy text-white border-vbc-navy shadow-md'
                : 'bg-white border-vbc-gray-light hover:border-vbc-blue/50 text-vbc-navy'
            }`}
          >
            <span className={`text-[10px] uppercase font-bold block ${severityFilter === 'ALL' ? 'text-gray-300' : 'text-vbc-gray'}`}>
              Total ACOs
            </span>
            <span className="text-xl font-black block mt-1">{counts.total}</span>
            <span className={`text-[9px] block mt-0.5 ${severityFilter === 'ALL' ? 'text-gray-300' : 'text-vbc-gray'}`}>
              100% Evaluated
            </span>
          </button>

          <button
            onClick={() => { setSeverityFilter('HIGH'); setCurrentPage(1); }}
            className={`p-3.5 rounded-xl border text-left transition-all ${
              severityFilter === 'HIGH'
                ? 'bg-vbc-red text-white border-vbc-red shadow-md'
                : 'bg-vbc-red-light/30 border-vbc-red/20 text-vbc-navy hover:border-vbc-red'
            }`}
          >
            <span className={`text-[10px] uppercase font-bold block ${severityFilter === 'HIGH' ? 'text-red-100' : 'text-vbc-red'}`}>
              High Severity
            </span>
            <span className="text-xl font-black block mt-1">{counts.high}</span>
            <span className={`text-[9px] block mt-0.5 ${severityFilter === 'HIGH' ? 'text-red-100' : 'text-vbc-red'}`}>
              Critical Anomaly
            </span>
          </button>

          <button
            onClick={() => { setSeverityFilter('MEDIUM'); setCurrentPage(1); }}
            className={`p-3.5 rounded-xl border text-left transition-all ${
              severityFilter === 'MEDIUM'
                ? 'bg-vbc-orange-dark text-white border-vbc-orange-dark shadow-md'
                : 'bg-vbc-orange-light/30 border-vbc-orange/20 text-vbc-navy hover:border-vbc-orange'
            }`}
          >
            <span className={`text-[10px] uppercase font-bold block ${severityFilter === 'MEDIUM' ? 'text-orange-100' : 'text-vbc-orange-dark'}`}>
              Medium Severity
            </span>
            <span className="text-xl font-black block mt-1">{counts.medium}</span>
            <span className={`text-[9px] block mt-0.5 ${severityFilter === 'MEDIUM' ? 'text-orange-100' : 'text-vbc-orange-dark'}`}>
              Moderate Risk
            </span>
          </button>

          <button
            onClick={() => { setSeverityFilter('LOW'); setCurrentPage(1); }}
            className={`p-3.5 rounded-xl border text-left transition-all ${
              severityFilter === 'LOW'
                ? 'bg-vbc-blue text-white border-vbc-blue shadow-md'
                : 'bg-blue-50 border-blue-200 text-vbc-navy hover:border-vbc-blue'
            }`}
          >
            <span className={`text-[10px] uppercase font-bold block ${severityFilter === 'LOW' ? 'text-blue-100' : 'text-vbc-blue'}`}>
              Low Severity
            </span>
            <span className="text-xl font-black block mt-1">{counts.low}</span>
            <span className={`text-[9px] block mt-0.5 ${severityFilter === 'LOW' ? 'text-blue-100' : 'text-vbc-blue'}`}>
              Mild Variation
            </span>
          </button>

          <button
            onClick={() => { setSeverityFilter('NORMAL'); setCurrentPage(1); }}
            className={`p-3.5 rounded-xl border text-left transition-all ${
              severityFilter === 'NORMAL'
                ? 'bg-vbc-green-dark text-white border-vbc-green-dark shadow-md'
                : 'bg-vbc-green-light/30 border-vbc-green/20 text-vbc-navy hover:border-vbc-green-dark'
            }`}
          >
            <span className={`text-[10px] uppercase font-bold block ${severityFilter === 'NORMAL' ? 'text-green-100' : 'text-vbc-green-dark'}`}>
              Normal ACOs
            </span>
            <span className="text-xl font-black block mt-1">{counts.normal}</span>
            <span className={`text-[9px] block mt-0.5 ${severityFilter === 'NORMAL' ? 'text-green-100' : 'text-vbc-green-dark'}`}>
              Stable Performance
            </span>
          </button>
        </div>

        {/* Search Bar & Controls */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3.5 rounded-xl border border-vbc-gray-light">
          <div className="relative flex-1">
            <Search size={15} className="absolute left-3 top-2.5 text-vbc-gray" />
            <input
              type="text"
              placeholder="Search by ACO Name, ACO ID (e.g. A1001, A1019), or metric..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full pl-9 pr-4 py-1.5 bg-gray-50 border border-vbc-gray-light rounded-lg text-xs text-vbc-navy placeholder:text-vbc-gray focus:outline-none focus:border-vbc-blue"
            />
          </div>

          <div className="text-[11px] text-vbc-gray font-semibold whitespace-nowrap">
            Showing {filtered.length > 0 ? pageStart + 1 : 0}–{Math.min(pageStart + PAGE_SIZE, filtered.length)} of {filtered.length} matching ACOs
          </div>
        </div>

        {/* Loading Spinner */}
        {loading ? (
          <div className="flex items-center justify-center h-64 text-vbc-gray bg-white rounded-xl border border-vbc-gray-light">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-vbc-blue"></div>
            <span className="ml-3 text-xs font-semibold">Running LOF Model evaluation across all ACOs for PY {selectedYear}...</span>
          </div>
        ) : (
          /* Cards Grid */
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {paginatedAlerts.map((alert) => (
              <div
                key={alert.id}
                className={`p-4 rounded-xl border transition-all ${
                  alert.status === 'reviewed'
                    ? 'bg-gray-50 border-gray-200 opacity-60'
                    : alert.severity === 'HIGH'
                    ? 'bg-vbc-red-light/40 border-vbc-red/25 hover:border-vbc-red'
                    : alert.severity === 'MEDIUM'
                    ? 'bg-vbc-orange-light/40 border-vbc-orange/25 hover:border-vbc-orange'
                    : alert.severity === 'LOW'
                    ? 'bg-blue-50/40 border-blue-200 hover:border-vbc-blue'
                    : 'bg-white border-vbc-gray-light hover:border-vbc-green-dark/40'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="space-y-1.5 flex-1 pr-2">
                    <div className="flex items-center space-x-2">
                      <span
                        className={`px-2 py-0.5 rounded text-[9px] font-extrabold border uppercase ${
                          alert.severity === 'HIGH'
                            ? 'bg-vbc-red-light text-vbc-red border-vbc-red/25'
                            : alert.severity === 'MEDIUM'
                            ? 'bg-vbc-orange-light text-vbc-orange-dark border-vbc-orange/25'
                            : alert.severity === 'LOW'
                            ? 'bg-blue-100 text-vbc-blue border-blue-300'
                            : 'bg-vbc-green-light text-vbc-green-dark border-vbc-green/25'
                        }`}
                      >
                        {alert.severity} SEVERITY
                      </span>

                      {alert.score !== undefined && (
                        <span className="text-[10px] font-bold text-vbc-gray">
                          Score: {alert.score}
                        </span>
                      )}

                      <span className="text-[10px] text-vbc-gray">PY {selectedYear}</span>
                    </div>

                    <button
                      onClick={() => navigate(`/aco/${alert.acoId}?year=${selectedYear}`)}
                      className="font-bold text-sm text-vbc-navy hover:text-vbc-blue transition-colors text-left flex items-center gap-1 group"
                    >
                      <span>{alert.aco} ({alert.acoId})</span>
                      <ChevronRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
                    </button>

                    <p className="text-[11px] font-medium text-vbc-navy/90 leading-relaxed">
                      <strong>{alert.metric}:</strong> {alert.explanation}
                    </p>

                    {alert.status === 'active' && (
                      <div className="p-2.5 bg-white/80 border border-black/5 rounded-lg text-[10px] text-vbc-navy space-y-1">
                        <div>
                          <strong>Recommended Action:</strong> {alert.recommendedAction}
                        </div>
                        {alert.savingsLoss !== undefined && (
                          <div className="text-[9.5px] text-vbc-gray">
                            Net Financial Impact: <span className={`font-bold ${alert.savingsLoss >= 0 ? 'text-vbc-green-dark' : 'text-vbc-red'}`}>${alert.savingsLoss >= 0 ? '+' : ''}{alert.savingsLoss.toLocaleString()}</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col items-end space-y-2">
                    {alert.status === 'active' && (
                      <button
                        onClick={() => handleResolve(alert.id)}
                        className="px-2 py-1 text-vbc-gray hover:text-vbc-blue font-semibold text-[10px] border border-vbc-gray-light rounded bg-white hover:bg-gray-50 transition-colors"
                      >
                        Resolve
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {filtered.length === 0 && (
              <div className="col-span-full text-center py-12 bg-white rounded-xl border border-vbc-gray-light text-vbc-gray space-y-2">
                <AlertTriangle size={24} className="mx-auto text-vbc-orange" />
                <p className="text-xs font-semibold">No ACO anomalies match the active filters.</p>
                <button
                  onClick={() => { setSeverityFilter('ALL'); setSearchQuery(''); }}
                  className="text-xs text-vbc-blue underline font-bold"
                >
                  Reset all filters
                </button>
              </div>
            )}
          </div>
        )}

        {/* Pagination Bar */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between bg-white p-3.5 rounded-xl border border-vbc-gray-light">
            <button
              disabled={currentPage === 1}
              onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
              className="px-3 py-1.5 border border-vbc-gray-light rounded-lg text-xs font-semibold text-vbc-navy hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1"
            >
              <ChevronLeft size={14} />
              Previous
            </button>

            <span className="text-xs font-bold text-vbc-navy">
              Page {currentPage} of {totalPages}
            </span>

            <button
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
              className="px-3 py-1.5 border border-vbc-gray-light rounded-lg text-xs font-semibold text-vbc-navy hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1"
            >
              Next
              <ChevronRight size={14} />
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default AlertsPage;
