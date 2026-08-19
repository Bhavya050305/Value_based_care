import React, { useState, useEffect } from 'react';
import { useDataMode } from '../context/DataModeContext';
import { useACO } from '../context/ACOContext';
import { usePageAIContext } from '../hooks/usePageAIContext';
import { Layout } from '../components/Layout';
import { reportService } from '../services/reportService';
import { forecastService } from '../services/forecastService';
import { peerTargetService } from '../services/peerTargetService';
import { PeerTargetProfile } from '../data/mock/peerTargetData';
import { FileBarChart, Download, FileText, CheckCircle2, Loader2 } from 'lucide-react';

type ReportKind = 'brief' | 'full';

export const ReportsPage: React.FC = () => {
  const { dataMode } = useDataMode();
  const { selectedAcoId, setSelectedAcoId, selectedYear, setSelectedYear, supportedYears, availableAcos } = useACO();

  const [peerTarget, setPeerTarget] = useState<PeerTargetProfile | null>(null);
  const [forecast, setForecast] = useState<any>(null);
  const [reportKind, setReportKind] = useState<ReportKind>('brief');
  const [generated, setGenerated] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    setGenerated(false);
    forecastService.getACOForecast(selectedAcoId, dataMode).then((res) => {
      if (res.success) setForecast(res.data);
    });
    peerTargetService.getPeerTarget(selectedAcoId, dataMode).then((res) => {
      if (res.success) setPeerTarget(res.data);
    });
  }, [selectedAcoId, dataMode]);

  const selectedAco = availableAcos.find((a) => a.aco_id === selectedAcoId || a.id === selectedAcoId);
  const acoDisplayName = selectedAco ? `${selectedAco.aco_id || selectedAco.id} — ${selectedAco.name}` : selectedAcoId;

  usePageAIContext(
    { page: 'Reports', route: '/reports', acoId: selectedAcoId, acoName: selectedAco?.name, year: selectedYear, reportKind },
    [selectedAcoId, selectedYear, reportKind]
  );

  const handleGenerate = async () => {
    setGenerating(true);
    await new Promise((r) => setTimeout(r, 600));
    setGenerating(false);
    setGenerated(true);
  };

  const handleDownload = async () => {
    setDownloading(true);
    try {
      await reportService.downloadACOReport(selectedAcoId, selectedYear);
    } catch (err) {
      console.error('Error downloading PDF report:', err);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <Layout title="Reports" acoId={selectedAcoId} acoName={selectedAco?.name} onLogout={() => {}}>
      <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <FileBarChart size={16} className="text-vbc-blue" />
          <h3 className="font-bold text-sm text-vbc-navy">Contract Manager Reports</h3>
        </div>
        <div className="flex items-center gap-3">
          <div className="space-y-1">
            <span className="text-[10px] uppercase font-bold text-vbc-gray block">Performance Year</span>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              className="bg-gray-50 border border-vbc-gray-light rounded-lg px-3 py-2 text-xs font-semibold text-vbc-navy focus:outline-none"
            >
              {supportedYears.map((yr) => (
                <option key={yr} value={yr}>
                  PY {yr}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-1">
            <span className="text-[10px] uppercase font-bold text-vbc-gray block">ACO Contract</span>
            <select
              value={selectedAcoId}
              onChange={(e) => setSelectedAcoId(e.target.value)}
              className="bg-gray-50 border border-vbc-gray-light rounded-lg px-3 py-2 text-xs font-semibold text-vbc-navy focus:outline-none max-w-[220px] truncate"
            >
              {availableAcos.length > 0 ? (
                availableAcos.map((a) => (
                  <option key={a.aco_id || a.id} value={a.aco_id || a.id}>
                    {a.aco_id || a.id} — {a.name}
                  </option>
                ))
              ) : (
                <option value={selectedAcoId}>{selectedAcoId}</option>
              )}
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <button
          onClick={() => setReportKind('brief')}
          className={`text-left p-5 rounded-xl border-2 transition-all space-y-2 ${
            reportKind === 'brief' ? 'border-vbc-blue bg-vbc-blue-light/30' : 'border-vbc-gray-light bg-white hover:border-vbc-gray'
          }`}
        >
          <div className="flex items-center justify-between">
            <h4 className="font-bold text-sm text-vbc-navy">Executive PDF Report</h4>
            {reportKind === 'brief' && <CheckCircle2 size={16} className="text-vbc-blue" />}
          </div>
          <p className="text-xs text-vbc-gray leading-relaxed">
            Multi-page executive PDF report formatted with ReportLab: financial performance, quality metrics, utilization, ML risk assessment, and grounded recommendations.
          </p>
        </button>

        <button
          onClick={() => setReportKind('full')}
          className={`text-left p-5 rounded-xl border-2 transition-all space-y-2 ${
            reportKind === 'full' ? 'border-vbc-blue bg-vbc-blue-light/30' : 'border-vbc-gray-light bg-white hover:border-vbc-gray'
          }`}
        >
          <div className="flex items-center justify-between">
            <h4 className="font-bold text-sm text-vbc-navy">Full Contract PDF Assessment</h4>
            {reportKind === 'full' && <CheckCircle2 size={16} className="text-vbc-blue" />}
          </div>
          <p className="text-xs text-vbc-gray leading-relaxed">
            Comprehensive contract assessment PDF with grounded AI recommendations, provider review questions, and detailed risk anomaly tables.
          </p>
        </button>
      </div>

      {reportKind === 'full' && (
        <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5">
          <h4 className="font-bold text-xs text-vbc-navy uppercase tracking-wider border-b border-vbc-gray-light pb-2 mb-3">
            Full PDF Report Included Sections
          </h4>
          <ol className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1.5 text-xs text-vbc-navy list-decimal pl-4">
            {reportService.fullReportPages.map((p, idx) => (
              <li key={idx}>{p}</li>
            ))}
          </ol>
        </div>
      )}

      {/* Executive brief preview */}
      {selectedAco && (
        <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-6 space-y-4">
          <div className="flex items-center space-x-2 border-b border-vbc-gray-light pb-2">
            <FileText size={15} className="text-vbc-blue" />
            <h4 className="font-bold text-xs text-vbc-navy uppercase tracking-wider">Report Metadata Target</h4>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div>
              <span className="text-[9px] uppercase font-bold text-vbc-gray block">ACO Contract</span>
              <span className="font-bold text-vbc-navy">{acoDisplayName}</span>
            </div>
            <div>
              <span className="text-[9px] uppercase font-bold text-vbc-gray block">Performance Year</span>
              <span className="font-bold text-vbc-navy">PY {selectedYear}</span>
            </div>
            <div>
              <span className="text-[9px] uppercase font-bold text-vbc-gray block">Format</span>
              <span className="font-bold text-vbc-blue">Server PDF (ReportLab)</span>
            </div>
            <div>
              <span className="text-[9px] uppercase font-bold text-vbc-gray block">Peer Target Savings</span>
              <span className="font-bold text-vbc-green-dark">{peerTarget ? `${peerTarget.targetSavingsRate.toFixed(2)}%` : '—'}</span>
            </div>
          </div>
        </div>
      )}

      <div className="bg-vbc-navy rounded-xl p-5 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p className="text-xs text-vbc-gray-light">
          {generated
            ? `Server PDF compiled for ACO ${selectedAcoId} (PY ${selectedYear}) — ready for download.`
            : `Click Generate Report to compile structured database intelligence into a PDF.`}
        </p>
        <div className="flex items-center space-x-3 flex-shrink-0">
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-white/10 text-white hover:bg-white/20 disabled:opacity-50 transition-colors"
          >
            {generating ? 'Compiling PDF Data...' : 'Generate Report'}
          </button>
          <button
            onClick={handleDownload}
            disabled={!generated || downloading}
            className="flex items-center space-x-1.5 px-4 py-2 rounded-lg text-xs font-semibold bg-vbc-blue hover:bg-vbc-blue-medium disabled:opacity-40 text-white transition-colors"
          >
            {downloading ? <Loader2 size={13} className="animate-spin" /> : <Download size={13} />}
            <span>{downloading ? 'Downloading PDF...' : `Download ${selectedAcoId} PDF Report`}</span>
          </button>
        </div>
      </div>
    </Layout>
  );
};

export default ReportsPage;
