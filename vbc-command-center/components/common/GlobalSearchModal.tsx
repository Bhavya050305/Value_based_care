import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X, Building2, User, Activity, MapPin, ArrowRight } from 'lucide-react';
import { usePreferenceStore } from '../../store/preferenceStore';
import { mockProviders } from '../../data/mock/providers';
import { mockACOs } from '../../data/mock/acos';
import { mockHospitals } from '../../data/mock/hospitals';

export const GlobalSearchModal: React.FC = () => {
  const { searchModalOpen, setSearchModalOpen } = usePreferenceStore();
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setSearchModalOpen(true);
      }
      if (e.key === 'Escape' && searchModalOpen) {
        setSearchModalOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [searchModalOpen, setSearchModalOpen]);

  if (!searchModalOpen) return null;

  const q = query.trim().toLowerCase();

  const matchingProviders = q
    ? mockProviders.filter(
        (p) =>
          p.providerName.toLowerCase().includes(q) ||
          p.npi.includes(q) ||
          p.providerType.toLowerCase().includes(q) ||
          p.state.toLowerCase().includes(q)
      )
    : [];

  const matchingACOs = q
    ? mockACOs.filter((a) => a.acoName.toLowerCase().includes(q) || a.acoId.toLowerCase().includes(q))
    : [];

  const matchingHospitals = q
    ? mockHospitals.filter(
        (h) => h.facilityName.toLowerCase().includes(q) || h.facilityId.includes(q) || h.state.toLowerCase().includes(q)
      )
    : [];

  const handleSelectProvider = (npi: string) => {
    setSearchModalOpen(false);
    setQuery('');
    navigate(`/providers/${npi}`);
  };

  const handleSelectAco = (acoId: string) => {
    setSearchModalOpen(false);
    setQuery('');
    navigate('/acos');
  };

  const handleSelectHospital = () => {
    setSearchModalOpen(false);
    setQuery('');
    navigate('/quality');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
        {/* Search Header */}
        <div className="flex items-center px-4 py-3.5 border-b border-slate-800 bg-slate-950/60">
          <Search className="w-5 h-5 text-blue-400 mr-3" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search provider NPI, name, ACO, facility ID, or state... (Ctrl+K)"
            className="flex-1 bg-transparent border-0 text-white placeholder-slate-500 focus:outline-none text-base font-sans"
            autoFocus
          />
          {query && (
            <button onClick={() => setQuery('')} className="p-1 text-slate-400 hover:text-white mr-2">
              <X className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={() => setSearchModalOpen(false)}
            className="px-2 py-1 text-xs bg-slate-800 text-slate-300 rounded border border-slate-700 hover:bg-slate-700"
          >
            ESC
          </button>
        </div>

        {/* Results List */}
        <div className="overflow-y-auto p-4 space-y-4 flex-1">
          {!q ? (
            <div className="text-center py-8 text-slate-500 text-sm">
              Type NPI, Provider name, ACO ID, Facility ID, or State abbreviation to search across the enterprise database.
            </div>
          ) : matchingProviders.length === 0 && matchingACOs.length === 0 && matchingHospitals.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-sm">
              No matching providers, ACOs, or facilities found for &quot;{query}&quot;.
            </div>
          ) : (
            <>
              {/* Providers */}
              {matchingProviders.length > 0 && (
                <div>
                  <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5 text-blue-400" />
                    Providers ({matchingProviders.length})
                  </div>
                  <div className="space-y-1">
                    {matchingProviders.map((p) => (
                      <div
                        key={p.npi}
                        onClick={() => handleSelectProvider(p.npi)}
                        className="flex items-center justify-between p-2.5 rounded-lg hover:bg-slate-800/80 cursor-pointer group border border-transparent hover:border-slate-700/60 transition-colors"
                      >
                        <div>
                          <div className="text-sm font-medium text-white group-hover:text-blue-400 flex items-center gap-2">
                            {p.providerName}
                            <span className="text-xs font-mono px-1.5 py-0.2 bg-slate-800 text-slate-400 rounded">
                              NPI: {p.npi}
                            </span>
                          </div>
                          <div className="text-xs text-slate-400 flex items-center gap-3 mt-0.5">
                            <span>{p.providerType}</span>
                            <span className="flex items-center gap-0.5">
                              <MapPin className="w-3 h-3 text-slate-500" /> {p.city}, {p.state}
                            </span>
                            <span>{p.totalBeneficiaries} Benes</span>
                          </div>
                        </div>
                        <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-blue-400 group-hover:translate-x-0.5 transition-all" />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ACOs */}
              {matchingACOs.length > 0 && (
                <div>
                  <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Building2 className="w-3.5 h-3.5 text-emerald-400" />
                    Accountable Care Organizations ({matchingACOs.length})
                  </div>
                  <div className="space-y-1">
                    {matchingACOs.map((a) => (
                      <div
                        key={a.acoId}
                        onClick={() => handleSelectAco(a.acoId)}
                        className="flex items-center justify-between p-2.5 rounded-lg hover:bg-slate-800/80 cursor-pointer group border border-transparent hover:border-slate-700/60 transition-colors"
                      >
                        <div>
                          <div className="text-sm font-medium text-white group-hover:text-emerald-400 flex items-center gap-2">
                            {a.acoName}
                            <span className="text-xs font-mono px-1.5 py-0.2 bg-slate-800 text-slate-400 rounded">
                              {a.acoId}
                            </span>
                          </div>
                          <div className="text-xs text-slate-400 flex items-center gap-3 mt-0.5">
                            <span>{a.riskModel}</span>
                            <span>Track: {a.currentTrack}</span>
                            <span>{a.assignedBeneficiaries.toLocaleString()} Benes</span>
                          </div>
                        </div>
                        <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-emerald-400 group-hover:translate-x-0.5 transition-all" />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Hospitals */}
              {matchingHospitals.length > 0 && (
                <div>
                  <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Activity className="w-3.5 h-3.5 text-rose-400" />
                    Hospitals & Safety Facilities ({matchingHospitals.length})
                  </div>
                  <div className="space-y-1">
                    {matchingHospitals.map((h) => (
                      <div
                        key={h.facilityId}
                        onClick={handleSelectHospital}
                        className="flex items-center justify-between p-2.5 rounded-lg hover:bg-slate-800/80 cursor-pointer group border border-transparent hover:border-slate-700/60 transition-colors"
                      >
                        <div>
                          <div className="text-sm font-medium text-white group-hover:text-rose-400 flex items-center gap-2">
                            {h.facilityName}
                            <span className="text-xs font-mono px-1.5 py-0.2 bg-slate-800 text-slate-400 rounded">
                              ID: {h.facilityId}
                            </span>
                          </div>
                          <div className="text-xs text-slate-400 flex items-center gap-3 mt-0.5">
                            <span>State: {h.state}</span>
                            <span>Quality: {h.overallQualityTier}</span>
                          </div>
                        </div>
                        <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-rose-400 group-hover:translate-x-0.5 transition-all" />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
