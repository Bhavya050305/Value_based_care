import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  Search,
  FileSpreadsheet,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  MapPin,
  CheckCircle2,
  AlertCircle,
  Filter,
} from 'lucide-react';
import { useProviders } from '../../hooks/useProviders';
import { ProviderRecord } from '../../types/provider';
import { GlobalFilterBar } from '../../components/filters/GlobalFilterBar';
import { StatusBadge } from '../../components/common/StatusBadge';
import { formatCurrency, formatNumber } from '../../utils/formatting';

export const ProviderExplorer: React.FC = () => {
  const navigate = useNavigate();
  const { providers, isLoading } = useProviders();

  // Sorting state
  const [sortField, setSortField] = useState<keyof ProviderRecord>('totalMedicarePaymentAmount');
  const [sortAsc, setSortAsc] = useState<boolean>(false);

  // Pagination state
  const [currentPage, setCurrentPage] = useState<number>(1);
  const pageSize = 5;

  const handleSort = (field: keyof ProviderRecord) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  const sortedProviders = [...providers].sort((a, b) => {
    let valA = a[sortField] ?? 0;
    let valB = b[sortField] ?? 0;
    if (typeof valA === 'string') valA = (valA as string).toLowerCase();
    if (typeof valB === 'string') valB = (valB as string).toLowerCase();

    if (valA < valB) return sortAsc ? -1 : 1;
    if (valA > valB) return sortAsc ? 1 : -1;
    return 0;
  });

  const totalPages = Math.ceil(sortedProviders.length / pageSize) || 1;
  const paginatedProviders = sortedProviders.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const exportCSV = () => {
    const headers = ['NPI', 'Provider Name', 'Provider Type', 'City', 'State', 'Beneficiaries', 'Services', 'Medicare Allowed ($)', 'Medicare Payment ($)', 'Standardized ($)', 'Avg Age', 'Risk Score', 'Performance Tier'];
    const rows = sortedProviders.map((p) => [
      p.npi,
      `"${p.providerName}"`,
      `"${p.providerType}"`,
      p.city,
      p.state,
      p.totalBeneficiaries,
      p.totalServices,
      p.totalMedicareAllowedAmount,
      p.totalMedicarePaymentAmount,
      p.totalMedicareStandardizedAmount,
      p.averageBeneficiaryAge,
      p.averageRiskScore,
      p.performanceTier,
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'Provider_Performance_Directory_2024.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">Provider Network Management</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">CMS Dataset 92396110</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mt-1">Provider Explorer</h1>
          <p className="text-xs text-slate-400 mt-1">
            Search, filter, and drill into individual provider cost metrics, service utilization, and beneficiary risk tiers.
          </p>
        </div>

        <button
          onClick={exportCSV}
          className="flex items-center gap-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg px-3 py-2 text-xs font-medium text-slate-200 transition-colors"
        >
          <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
          <span>Export Provider Directory CSV</span>
        </button>
      </div>

      {/* Global Filter Bar */}
      <GlobalFilterBar />

      {/* Provider Table Card */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950/60">
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-blue-400" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Contracted Provider Directory</h2>
            <span className="text-xs font-mono px-2 py-0.5 bg-slate-800 text-slate-300 rounded-full">
              Showing {sortedProviders.length} Providers
            </span>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="p-3.5 cursor-pointer hover:text-white" onClick={() => handleSort('providerName')}>
                  <div className="flex items-center gap-1">Provider Name & NPI <ArrowUpDown className="w-3 h-3 text-slate-600" /></div>
                </th>
                <th className="p-3.5">Provider Type</th>
                <th className="p-3.5">Location</th>
                <th className="p-3.5 text-right cursor-pointer hover:text-white" onClick={() => handleSort('totalBeneficiaries')}>
                  <div className="flex items-center justify-end gap-1">Benes <ArrowUpDown className="w-3 h-3 text-slate-600" /></div>
                </th>
                <th className="p-3.5 text-right cursor-pointer hover:text-white" onClick={() => handleSort('totalServices')}>
                  <div className="flex items-center justify-end gap-1">Services <ArrowUpDown className="w-3 h-3 text-slate-600" /></div>
                </th>
                <th className="p-3.5 text-right cursor-pointer hover:text-white" onClick={() => handleSort('totalMedicareAllowedAmount')}>
                  <div className="flex items-center justify-end gap-1">Medicare Allowed <ArrowUpDown className="w-3 h-3 text-slate-600" /></div>
                </th>
                <th className="p-3.5 text-right cursor-pointer hover:text-white" onClick={() => handleSort('totalMedicarePaymentAmount')}>
                  <div className="flex items-center justify-end gap-1">Medicare Payment <ArrowUpDown className="w-3 h-3 text-slate-600" /></div>
                </th>
                <th className="p-3.5 text-right cursor-pointer hover:text-white" onClick={() => handleSort('averageRiskScore')}>
                  <div className="flex items-center justify-end gap-1">Risk Score <ArrowUpDown className="w-3 h-3 text-slate-600" /></div>
                </th>
                <th className="p-3.5 text-center">Performance</th>
                <th className="p-3.5 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {isLoading ? (
                <tr>
                  <td colSpan={10} className="p-8 text-center text-slate-500">Loading provider records...</td>
                </tr>
              ) : paginatedProviders.length === 0 ? (
                <tr>
                  <td colSpan={10} className="p-8 text-center text-slate-400">
                    No provider records match your search or filter criteria. Try resetting filters.
                  </td>
                </tr>
              ) : (
                paginatedProviders.map((provider) => (
                  <tr
                    key={provider.npi}
                    onClick={() => navigate(`/providers/${provider.npi}`)}
                    className="hover:bg-slate-800/50 cursor-pointer transition-colors group"
                  >
                    <td className="p-3.5">
                      <div className="font-semibold text-white group-hover:text-blue-400 transition-colors">
                        {provider.providerName}
                      </div>
                      <div className="text-[11px] font-mono text-slate-400 flex items-center gap-2">
                        <span>NPI: {provider.npi}</span>
                        {provider.medicareParticipating && (
                          <span className="text-[10px] text-emerald-400 bg-emerald-950/60 px-1 rounded">Participating</span>
                        )}
                      </div>
                    </td>
                    <td className="p-3.5 text-slate-300 font-medium">{provider.providerType}</td>
                    <td className="p-3.5 text-slate-400">
                      <div className="flex items-center gap-1 text-slate-300">
                        <MapPin className="w-3 h-3 text-slate-500" />
                        {provider.city}, {provider.state}
                      </div>
                    </td>
                    <td className="p-3.5 text-right font-mono text-slate-200">{formatNumber(provider.totalBeneficiaries)}</td>
                    <td className="p-3.5 text-right font-mono text-slate-200">{formatNumber(provider.totalServices)}</td>
                    <td className="p-3.5 text-right font-mono text-slate-300">{formatCurrency(provider.totalMedicareAllowedAmount)}</td>
                    <td className="p-3.5 text-right font-mono font-bold text-white">{formatCurrency(provider.totalMedicarePaymentAmount)}</td>
                    <td className={`p-3.5 text-right font-mono font-semibold ${provider.averageRiskScore > 1.4 ? 'text-rose-400' : 'text-slate-200'}`}>
                      {provider.averageRiskScore}
                    </td>
                    <td className="p-3.5 text-center">
                      <StatusBadge status={provider.performanceTier || 'Moderate'} size="sm" />
                    </td>
                    <td className="p-3.5 text-center">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/providers/${provider.npi}`);
                        }}
                        className="px-2.5 py-1 text-[11px] bg-slate-800 group-hover:bg-blue-600 text-slate-200 group-hover:text-white rounded border border-slate-700 transition-colors flex items-center gap-1 mx-auto"
                      >
                        Details <ExternalLink className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="p-3.5 border-t border-slate-800 bg-slate-950/60 flex items-center justify-between text-xs text-slate-400">
          <div>
            Showing <strong className="text-white">{(currentPage - 1) * pageSize + 1}</strong> to{' '}
            <strong className="text-white">{Math.min(currentPage * pageSize, sortedProviders.length)}</strong> of{' '}
            <strong className="text-white">{sortedProviders.length}</strong> providers
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
              disabled={currentPage === 1}
              className="p-1.5 rounded bg-slate-900 border border-slate-800 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono px-2">Page {currentPage} of {totalPages}</span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="p-1.5 rounded bg-slate-900 border border-slate-800 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
