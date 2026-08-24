import React from 'react';
import { PerformanceDriver } from '../types';
import StatusBadge from './StatusBadge';
import { AlertTriangle, ArrowDown, ArrowUp, CheckCircle2 } from 'lucide-react';

interface PerformanceDriversProps {
  drivers: PerformanceDriver[];
}

// Communicates drivers through metrics and severity badges only — no
// distributed per-row explanation panels. Ask the Global AI Assistant
// (bottom-right) for narrative context on any driver.
export const PerformanceDrivers: React.FC<PerformanceDriversProps> = ({
  drivers
}) => {
  return (
    <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-6 space-y-5">
      <div className="border-b border-vbc-gray-light pb-4">
        <h3 className="text-lg font-bold text-vbc-navy">ACO Performance Drivers</h3>
        <p className="text-xs text-vbc-gray mt-0.5">
          Key factors contributing to cost, quality, and clinical variance relative to peer benchmarks.
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-vbc-gray-light text-xs font-bold text-vbc-gray bg-gray-50">
              <th className="p-3">Performance Driver</th>
              <th className="p-3">Current</th>
              <th className="p-3">Peer Bench</th>
              <th className="p-3">Variance</th>
              <th className="p-3">Risk Impact</th>
              <th className="p-3">Severity</th>
            </tr>
          </thead>
          <tbody className="text-xs divide-y divide-vbc-gray-light">
            {drivers.map((drv, idx) => {
              const diffVal = drv.current - drv.peer;
              const isPmpmOrCost = drv.name.toLowerCase().includes('cost') || drv.name.toLowerCase().includes('utilization') || drv.name.toLowerCase().includes('pmpm') || drv.name.toLowerCase().includes('variation') || drv.name.toLowerCase().includes('readmission');
              
              // Direction check: higher is bad for cost/ER/readmissions, higher is good for preventive/experience
              const isNegativeDirection = isPmpmOrCost ? diffVal > 0 : diffVal < 0;
              const varianceText = diffVal > 0 ? `+${diffVal.toFixed(1)}%` : `${diffVal.toFixed(1)}%`;
              
              return (
                <tr key={idx} className="hover:bg-vbc-blue-light/30 transition-colors">
                  <td className="p-3 font-semibold text-vbc-navy">
                    {drv.name}
                  </td>
                  <td className="p-3 text-vbc-navy font-medium">
                    {drv.current.toFixed(1)}%
                  </td>
                  <td className="p-3 text-vbc-gray">
                    {drv.peer.toFixed(1)}%
                  </td>
                  <td className="p-3">
                    <span className={`inline-flex items-center font-bold ${
                      isNegativeDirection ? 'text-vbc-red-dark' : 'text-vbc-green-dark'
                    }`}>
                      {isNegativeDirection ? (
                        <ArrowUp size={12} className="mr-0.5" />
                      ) : (
                        <ArrowDown size={12} className="mr-0.5" />
                      )}
                      {varianceText}
                    </span>
                  </td>
                  <td className="p-3">
                    <StatusBadge type="priority" value={drv.impact} />
                  </td>
                  <td className="p-3">
                    <span className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-semibold border ${
                      isNegativeDirection 
                        ? 'bg-vbc-red-light text-vbc-red border-vbc-red/20' 
                        : 'bg-vbc-green-light text-vbc-green border-vbc-green/20'
                    }`}>
                      {isNegativeDirection ? (
                        <AlertTriangle size={10} />
                      ) : (
                        <CheckCircle2 size={10} />
                      )}
                      <span>{isNegativeDirection ? 'ADVERSE' : 'FAVORABLE'}</span>
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
export default PerformanceDrivers;
