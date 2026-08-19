import React, { useState } from 'react';
import { useDataMode } from '../context/DataModeContext';
import { useACO } from '../context/ACOContext';
import { reportService } from '../services/reportService';
import { Download, AlertCircle, Menu, RefreshCw, Loader2 } from 'lucide-react';

interface HeaderProps {
  title: string;
  onDownloadReport?: () => void;
  onMenuToggle?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  onDownloadReport,
  onMenuToggle
}) => {
  const { dataMode, setDataMode } = useDataMode();
  const { selectedAcoId, setSelectedAcoId, selectedYear, setSelectedYear, supportedYears, availableAcos } = useACO();
  const [downloading, setDownloading] = useState(false);

  const handleDownload = async () => {
    if (onDownloadReport) {
      onDownloadReport();
      return;
    }
    setDownloading(true);
    try {
      await reportService.downloadACOReport(selectedAcoId, selectedYear);
    } catch (err) {
      console.error('Error downloading report:', err);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <header className="sticky top-0 bg-white border-b border-vbc-gray-light z-20 h-16 flex flex-col justify-center px-4 md:px-6">
      <div className="flex items-center justify-between">
        
        {/* Mobile Hamburger menu & Title */}
        <div className="flex items-center space-x-3 lg:space-x-0">
          <button
            onClick={onMenuToggle}
            className="lg:hidden p-1.5 hover:bg-vbc-gray-light rounded-lg text-vbc-navy"
          >
            <Menu size={20} />
          </button>
          
          <h2 className="font-extrabold text-vbc-navy text-sm md:text-base truncate max-w-[200px] md:max-w-md">
            {title}
          </h2>
        </div>

        {/* Global Toolbar actions */}
        <div className="flex items-center space-x-2 md:space-x-3">
          {/* ACO Selector */}
          <div className="hidden md:block">
            <select
              value={selectedAcoId}
              onChange={(e) => setSelectedAcoId(e.target.value)}
              className="bg-gray-50 border border-vbc-gray-light hover:border-vbc-gray rounded-lg px-2.5 py-1.5 text-xs text-vbc-navy font-semibold focus:outline-none max-w-[150px] truncate"
            >
              {availableAcos.length > 0 ? (
                availableAcos.map((aco) => (
                  <option key={aco.aco_id || aco.id} value={aco.aco_id || aco.id}>
                    {aco.aco_id || aco.id} — {aco.name}
                  </option>
                ))
              ) : (
                <option value={selectedAcoId}>{selectedAcoId}</option>
              )}
            </select>
          </div>

          {/* Performance Year Selector */}
          <div>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              className="bg-gray-50 border border-vbc-gray-light hover:border-vbc-gray rounded-lg px-2.5 py-1.5 text-xs text-vbc-navy font-semibold focus:outline-none"
            >
              {supportedYears.map((yr) => (
                <option key={yr} value={yr}>
                  PY {yr}
                </option>
              ))}
            </select>
          </div>

          {/* Data Mode toggle */}
          <div className="flex items-center border border-vbc-gray-light p-0.5 rounded-lg bg-vbc-gray-light">
            <button
              onClick={() => setDataMode('demo')}
              className={`px-2 py-1 text-[10px] font-bold uppercase rounded-md transition-all ${
                dataMode === 'demo'
                  ? 'bg-vbc-blue text-white shadow-sm'
                  : 'text-vbc-gray hover:text-vbc-navy'
              }`}
            >
              Demo Data
            </button>
            <button
              onClick={() => setDataMode('connected')}
              className={`px-2 py-1 text-[10px] font-bold uppercase rounded-md transition-all flex items-center space-x-1 ${
                dataMode === 'connected'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-vbc-gray hover:text-vbc-navy'
              }`}
            >
              <RefreshCw size={10} className={dataMode === 'connected' ? 'animate-spin' : ''} />
              <span>Connected</span>
            </button>
          </div>

          {/* Download Report Button */}
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="flex items-center space-x-1.5 bg-vbc-blue hover:bg-vbc-blue-medium text-white px-3 py-1.5 rounded-lg text-xs font-semibold shadow-sm transition-all disabled:opacity-50"
          >
            {downloading ? (
              <Loader2 size={13} className="animate-spin" />
            ) : (
              <Download size={13} />
            )}
            <span className="hidden md:inline">{downloading ? 'Generating PDF...' : 'Download PDF Report'}</span>
          </button>
        </div>
      </div>

      {/* Banner indicator if Connected Mode is selected */}
      {dataMode === 'connected' && (
        <div className="absolute top-16 left-0 right-0 bg-emerald-50 border-b border-emerald-200 py-2 px-6 flex items-center justify-between text-xs text-emerald-800 animate-slideDown shadow-sm">
          <div className="flex items-center space-x-2">
            <AlertCircle size={16} className="text-emerald-600 animate-pulse" />
            <span>
              <strong>Connected Mode Active:</strong> Scoped strictly to <strong>ACO {selectedAcoId} — PY {selectedYear}</strong> via FastAPI backend & Supabase DB.
            </span>
          </div>
          <button
            onClick={() => setDataMode('demo')}
            className="font-bold underline text-emerald-800 hover:text-emerald-900 text-[11px]"
          >
            Switch to Demo Mode
          </button>
        </div>
      )}
    </header>
  );
};
export default Header;
