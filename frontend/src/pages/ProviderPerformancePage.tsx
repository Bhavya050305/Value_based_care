import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useDataMode } from '../context/DataModeContext';
import { useACO } from '../context/ACOContext';
import { usePageAIContext } from '../hooks/usePageAIContext';
import { Layout } from '../components/Layout';
import { StatusBadge } from '../components/StatusBadge';
import { ProviderVariationChart } from '../components/ProviderVariationChart';
import { acoService } from '../services/acoService';
import { providerService } from '../services/providerService';
import { ACO, Provider } from '../types';
import { Users } from 'lucide-react';

export const ProviderPerformancePage: React.FC = () => {
  const { dataMode } = useDataMode();
  const { selectedAcoId, setSelectedAcoId, availableAcos, selectedYear } = useACO();
  const [searchParams] = useSearchParams();
  const [acos, setAcos] = useState<ACO[]>([]);
  const [acoId, setAcoId] = useState(searchParams.get('aco') || selectedAcoId || 'A1001');
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (selectedAcoId && selectedAcoId !== acoId && !searchParams.get('aco')) {
      setAcoId(selectedAcoId);
    }
  }, [selectedAcoId]);

  useEffect(() => {
    acoService.getACOs(dataMode, selectedYear).then((res) => {
      if (res.success && res.data && res.data.length > 0) {
        setAcos(res.data);
        if (!acoId || acoId === 'abc-aco') {
          setAcoId(res.data[0].id);
        }
      }
    });
  }, [dataMode, selectedYear]);

  useEffect(() => {
    setLoading(true);
    providerService.getProviders(acoId, dataMode).then((res) => {
      if (res.success) setProviders(res.data);
      setLoading(false);
    });
  }, [acoId, dataMode]);

  const selectedAco = acos.find((a) => a.id === acoId);

  usePageAIContext(
    { page: 'Provider Performance', route: '/providers', acoId, acoName: selectedAco?.name, providerData: providers },
    [acoId, providers.length]
  );

  return (
    <Layout title="Provider Performance" acoId={acoId} acoName={selectedAco?.name} onLogout={() => {}}>
      <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <Users size={16} className="text-vbc-blue" />
          <h3 className="font-bold text-sm text-vbc-navy">Provider Panel by ACO</h3>
        </div>
        <select
          value={acoId}
          onChange={(e) => {
            setAcoId(e.target.value);
            setSelectedAcoId(e.target.value);
          }}
          className="bg-gray-50 border border-vbc-gray-light rounded-lg px-3 py-2 text-xs font-semibold text-vbc-navy focus:outline-none"
        >
          {availableAcos.length > 0 ? (
            availableAcos.map((a) => (
              <option key={a.aco_id || a.id} value={a.aco_id || a.id}>
                {a.name || a.aco_id || a.id} ({a.aco_id || a.id})
              </option>
            ))
          ) : (
            acos.map((a) => (
              <option key={a.id} value={a.id}>{a.name} ({a.id})</option>
            ))
          )}
        </select>
      </div>

      {loading ? (
        <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-10 text-center text-xs text-vbc-gray">Loading provider data...</div>
      ) : (
        <>
          <ProviderVariationChart providers={providers} />

          <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-6 space-y-4">
            <div className="border-b border-vbc-gray-light pb-2">
              <h4 className="font-bold text-xs text-vbc-navy uppercase tracking-wider">Full Clinician Panel Metrics</h4>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-vbc-gray-light text-xs font-bold text-vbc-gray bg-gray-50/50">
                    <th className="p-3">Provider</th>
                    <th className="p-3">Specialty</th>
                    <th className="p-3">Attributed Members</th>
                    <th className="p-3">Actual PMPM</th>
                    <th className="p-3">Benchmark PMPM</th>
                    <th className="p-3">Variance</th>
                    <th className="p-3 text-right">Risk Flag</th>
                  </tr>
                </thead>
                <tbody className="text-xs divide-y divide-vbc-gray-light">
                  {providers.map((p, idx) => (
                    <tr key={idx} className={`hover:bg-vbc-blue-light/35 transition-colors ${p.variance > 15 ? 'bg-vbc-red-light/20' : ''}`}>
                      <td className="p-3 font-semibold text-vbc-navy">{p.name}</td>
                      <td className="p-3 text-vbc-gray">{p.specialty}</td>
                      <td className="p-3 text-vbc-navy font-semibold">{p.attributedMembers.toLocaleString()}</td>
                      <td className="p-3 font-bold text-vbc-navy">${p.actualPMPM.toFixed(2)}</td>
                      <td className="p-3 text-vbc-gray">${p.peerPMPM.toFixed(2)}</td>
                      <td className={`p-3 font-bold ${p.variance > 10 ? 'text-vbc-red-dark' : 'text-vbc-green-dark'}`}>
                        {p.variance > 0 ? '+' : ''}{p.variance.toFixed(1)}%
                      </td>
                      <td className="p-3 text-right"><StatusBadge type="risk" value={p.riskFlag} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </Layout>
  );
};

export default ProviderPerformancePage;
