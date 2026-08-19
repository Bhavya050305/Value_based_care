import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useDataMode } from '../context/DataModeContext';
import { usePageAIContext } from '../hooks/usePageAIContext';
import { acoService } from '../services/acoService';
import { providerService } from '../services/providerService';
import { memberService } from '../services/memberService';
import { analyticsService } from '../services/analyticsService';
import { ACO, Provider, MemberRisk } from '../types';
import { Layout } from '../components/Layout';
import { StatusBadge } from '../components/StatusBadge';
import { ProviderVariationChart } from '../components/ProviderVariationChart';
import { MemberRiskChart } from '../components/MemberRiskChart';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { reportService } from '../services/reportService';
import { ChevronLeft, Download, Loader2, Building, Shield, FileText } from 'lucide-react';
import { useACO } from '../context/ACOContext';

type TabId = 'overview' | 'providers' | 'members';

export const ACODetail: React.FC = () => {
  const { acoId } = useParams<{ acoId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { dataMode } = useDataMode();
  const { selectedYear, setSelectedYear, selectedAcoId, setSelectedAcoId } = useACO();

  const yearFromQuery = searchParams.get('year');
  const effectiveYear = yearFromQuery && [2022, 2023, 2024].includes(Number(yearFromQuery))
    ? Number(yearFromQuery)
    : selectedYear;

  useEffect(() => {
    if (acoId && acoId !== selectedAcoId) {
      setSelectedAcoId(acoId);
    }
  }, [acoId]);

  useEffect(() => {
    if (yearFromQuery && Number(yearFromQuery) !== selectedYear && [2022, 2023, 2024].includes(Number(yearFromQuery))) {
      setSelectedYear(Number(yearFromQuery));
    }
  }, [yearFromQuery]);

  const [activeTab, setActiveTab] = useState<TabId>('overview');

  // Essential Domain state
  const [aco, setAco] = useState<ACO | null>(null);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [memberRisk, setMemberRisk] = useState<MemberRisk | null>(null);

  // Charts data
  const [financialTrend, setFinancialTrend] = useState<any[]>([]);
  const [qualityTrend, setQualityTrend] = useState<any[]>([]);

  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  const handleDownloadPdf = async () => {
    if (!aco) return;
    setDownloading(true);
    try {
      await reportService.downloadACOReport(aco.id, effectiveYear);
    } finally {
      setDownloading(false);
    }
  };

  // Fetch essential ACO performance details (Information-Only Scope)
  useEffect(() => {
    const loadDetails = async () => {
      if (!acoId) return;
      setLoading(true);
      try {
        const id = acoId;
        const [
          acoResponse,
          provResponse,
          memResponse,
          finTrendResponse,
          qualTrendResponse
        ] = await Promise.all([
          acoService.getACOById(id, dataMode, effectiveYear),
          providerService.getProviders(id, dataMode),
          memberService.getMemberRisk(id, dataMode),
          analyticsService.getACOFinancialTrend(id, dataMode, effectiveYear),
          analyticsService.getACOQualityTrend(id, dataMode, effectiveYear)
        ]);

        if (acoResponse.success) setAco(acoResponse.data);
        else setAco(null);

        if (provResponse.success) setProviders(provResponse.data);
        if (memResponse.success) setMemberRisk(memResponse.data);
        if (finTrendResponse.success) setFinancialTrend(finTrendResponse.data);
        if (qualTrendResponse.success) setQualityTrend(qualTrendResponse.data);
      } catch (err) {
        console.error('Error loading ACO details page:', err);
      } finally {
        setLoading(false);
      }
    };
    loadDetails();
  }, [acoId, dataMode, effectiveYear]);

  // Ground the Global AI Assistant in this ACO's structured context.
  usePageAIContext(
    {
      page: 'ACO Information Detail',
      route: `/aco/${acoId}`,
      acoId: aco?.id,
      acoName: aco?.name,
      riskLevel: aco?.riskLevel,
      year: effectiveYear,
      financial: aco
        ? {
            savingsLoss: aco.savingsLoss,
            actualPMPM: aco.actualPMPM,
            benchmarkPMPM: aco.riskAdjustedBenchmarkPMPM,
            totalExpenditure: aco.totalExpenditure,
          }
        : undefined,
      qualityScore: aco?.qualityScore,
    },
    [aco?.id, effectiveYear]
  );

  if (loading) {
    return (
      <Layout title="ACO Contract Detail" onLogout={() => {}}>
        <div className="flex items-center justify-center h-64 text-vbc-gray">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-vbc-blue"></div>
          <span className="ml-3 text-xs font-semibold">Retrieving ACO contract records from database for PY {effectiveYear}...</span>
        </div>
      </Layout>
    );
  }

  if (!aco) {
    return (
      <Layout title="ACO Contract Detail" onLogout={() => {}}>
        <div className="text-center py-12 bg-white rounded-xl border border-vbc-gray-light shadow-card p-8 space-y-4">
          <div className="text-vbc-red-dark font-bold text-base">ACO Not Found</div>
          <p className="text-xs text-vbc-gray max-w-md mx-auto">
            No database performance record exists for ACO <span className="font-mono font-bold text-vbc-navy">{acoId}</span> in Performance Year {effectiveYear}.
          </p>
          <button
            onClick={() => navigate('/explorer')}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-vbc-blue text-white text-xs font-bold rounded-lg shadow-sm hover:bg-vbc-blue-medium transition-colors cursor-pointer"
          >
            <ChevronLeft size={16} />
            <span>Return to ACO Explorer</span>
          </button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title={`ACO Contract: ${aco.name}`} acoId={aco.id} acoName={aco.name} onLogout={() => {}}>
      <div className="space-y-6">
        
        {/* Top Header Card */}
        <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-6 flex flex-col lg:flex-row justify-between lg:items-center space-y-4 lg:space-y-0">
          <div className="space-y-2">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => navigate('/explorer')}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-lg text-xs font-bold text-vbc-navy transition-colors cursor-pointer"
                title="Back to ACO Explorer"
              >
                <ChevronLeft size={16} />
                <span>Back to ACO Explorer</span>
              </button>
              <h1 className="text-xl font-bold text-vbc-navy">{aco.name}</h1>
              <StatusBadge type="risk" value={aco.riskLevel} />
            </div>
            
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-vbc-gray">
              <span>ACO ID: <strong className="text-vbc-navy font-mono">{aco.id}</strong></span>
              <span>State: <strong className="text-vbc-navy">{aco.state}</strong></span>
              <span>Track: <strong className="text-vbc-navy">{aco.track}</strong></span>
              <span>Risk Model: <strong className="text-vbc-navy">{aco.riskModel || 'Two-Sided Risk'}</strong></span>
              <div className="flex items-center space-x-1.5">
                <span>Performance Year:</span>
                <select
                  value={effectiveYear}
                  onChange={(e) => navigate(`/aco/${aco.id}?year=${e.target.value}`)}
                  className="bg-blue-50 border border-blue-200 rounded px-2 py-0.5 text-xs font-bold text-vbc-blue focus:outline-none focus:ring-1 focus:ring-vbc-blue cursor-pointer"
                >
                  <option value={2022}>PY 2022</option>
                  <option value={2023}>PY 2023</option>
                  <option value={2024}>PY 2024</option>
                </select>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center space-x-6 bg-gray-50 border border-vbc-gray-light/80 p-3 rounded-xl">
              <div>
                <span className="text-[10px] uppercase font-bold text-vbc-gray block">Quality Score</span>
                <span className="text-lg font-bold text-vbc-navy">{aco.qualityScore}%</span>
              </div>
              <div className="h-8 w-px bg-vbc-gray-light"></div>
              <div>
                <span className="text-[10px] uppercase font-bold text-vbc-gray block">Attributed Members</span>
                <span className="text-lg font-bold text-vbc-navy">{(aco.attributedMembers ?? 0).toLocaleString()}</span>
              </div>
              <div className="h-8 w-px bg-vbc-gray-light"></div>
              <div>
                <span className="text-[10px] uppercase font-bold text-vbc-gray block">Gross Savings / Loss</span>
                <span className={`text-lg font-bold ${(aco.savingsLoss ?? 0) < 0 ? 'text-vbc-red-dark' : 'text-vbc-green-dark'}`}>
                  ${Math.abs(aco.savingsLoss ?? 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </span>
              </div>
            </div>

            <button
              onClick={handleDownloadPdf}
              disabled={downloading}
              className="inline-flex items-center space-x-2 px-4 py-2.5 bg-vbc-blue text-white text-xs font-bold rounded-xl shadow-sm hover:bg-vbc-blue-medium disabled:opacity-50 transition-all cursor-pointer"
            >
              {downloading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  <span>Generating PDF...</span>
                </>
              ) : (
                <>
                  <Download size={16} />
                  <span>Download Information Report</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-vbc-gray-light flex space-x-8">
          <button
            onClick={() => setActiveTab('overview')}
            className={`pb-3 text-xs font-bold transition-all relative cursor-pointer ${
              activeTab === 'overview' ? 'text-vbc-blue border-b-2 border-vbc-blue' : 'text-vbc-gray hover:text-vbc-navy'
            }`}
          >
            Executive Summary & Financial Metrics
          </button>
          <button
            onClick={() => setActiveTab('providers')}
            className={`pb-3 text-xs font-bold transition-all relative cursor-pointer ${
              activeTab === 'providers' ? 'text-vbc-blue border-b-2 border-vbc-blue' : 'text-vbc-gray hover:text-vbc-navy'
            }`}
          >
            Clinician Panel Metrics ({providers.length})
          </button>
          <button
            onClick={() => setActiveTab('members')}
            className={`pb-3 text-xs font-bold transition-all relative cursor-pointer ${
              activeTab === 'members' ? 'text-vbc-blue border-b-2 border-vbc-blue' : 'text-vbc-gray hover:text-vbc-navy'
            }`}
          >
            Attributed Member Population Risk
          </button>
        </div>

        {/* TAB 1: EXECUTIVE SUMMARY & FINANCIAL METRICS */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* KPI Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-xl border border-vbc-gray-light p-4 shadow-card">
                <span className="text-xs font-semibold text-vbc-gray block">Benchmark PMPM</span>
                <span className="text-xl font-bold text-vbc-navy mt-1 block">${aco.riskAdjustedBenchmarkPMPM.toFixed(2)}</span>
                <span className="text-[10px] text-vbc-gray">PY {effectiveYear} CMS Benchmark</span>
              </div>
              <div className="bg-white rounded-xl border border-vbc-gray-light p-4 shadow-card">
                <span className="text-xs font-semibold text-vbc-gray block">Actual PMPM</span>
                <span className="text-xl font-bold text-vbc-navy mt-1 block">${aco.actualPMPM.toFixed(2)}</span>
                <span className="text-[10px] text-vbc-gray">Per Member Per Month Spend</span>
              </div>
              <div className="bg-white rounded-xl border border-vbc-gray-light p-4 shadow-card">
                <span className="text-xs font-semibold text-vbc-gray block">PMPM Variance</span>
                <span className={`text-xl font-bold mt-1 block ${aco.actualPMPM > aco.riskAdjustedBenchmarkPMPM ? 'text-vbc-red-dark' : 'text-vbc-green-dark'}`}>
                  ${(aco.actualPMPM - aco.riskAdjustedBenchmarkPMPM).toFixed(2)}
                </span>
                <span className="text-[10px] text-vbc-gray">Actual vs Benchmark</span>
              </div>
              <div className="bg-white rounded-xl border border-vbc-gray-light p-4 shadow-card">
                <span className="text-xs font-semibold text-vbc-gray block">Savings Rate</span>
                <span className={`text-xl font-bold mt-1 block ${aco.savingsLossPercent < 0 ? 'text-vbc-red-dark' : 'text-vbc-green-dark'}`}>
                  {aco.savingsLossPercent > 0 ? '+' : ''}{aco.savingsLossPercent}%
                </span>
                <span className="text-[10px] text-vbc-gray">Gross Savings Percentage</span>
              </div>
            </div>

            {/* Financial Trend vs Quality Chart Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl border border-vbc-gray-light p-5 shadow-card space-y-3">
                <h3 className="font-bold text-sm text-vbc-navy">Performance Year {effectiveYear} Expenditure Record</h3>
                <div className="h-56">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={financialTrend}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                      <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#64748B' }} />
                      <YAxis tick={{ fontSize: 11, fill: '#64748B' }} tickFormatter={(v) => `$${(v / 1e6).toFixed(0)}M`} />
                      <Tooltip formatter={(v: any) => [`$${(v / 1e6).toFixed(1)}M`, 'Value']} />
                      <Legend wrapperStyle={{ fontSize: '11px' }} />
                      <Line type="monotone" dataKey="benchmarkExpenditure" name="Benchmark Expenditure" stroke="#3B82F6" strokeWidth={2.5} />
                      <Line type="monotone" dataKey="actualExpenditure" name="Actual Expenditure" stroke="#64748B" strokeWidth={2.5} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-vbc-gray-light p-5 shadow-card space-y-3">
                <h3 className="font-bold text-sm text-vbc-navy">Quality Performance Score</h3>
                <div className="h-56">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={qualityTrend}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                      <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#64748B' }} />
                      <YAxis domain={[60, 100]} tick={{ fontSize: 11, fill: '#64748B' }} />
                      <Tooltip formatter={(v: any) => [`${v}%`, 'Quality Score']} />
                      <Legend wrapperStyle={{ fontSize: '11px' }} />
                      <Line type="monotone" dataKey="qualityScore" name="Quality Score %" stroke="#10B981" strokeWidth={2.5} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Detailed Contract Information Table */}
            <div className="bg-white rounded-xl border border-vbc-gray-light shadow-card p-5 space-y-4">
              <div className="flex items-center space-x-2 border-b border-vbc-gray-light pb-2">
                <Building size={16} className="text-vbc-blue" />
                <h3 className="font-bold text-sm text-vbc-navy">ACO Contract &amp; Database Record Information</h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
                <div className="p-3.5 bg-gray-50 rounded-lg border border-vbc-gray-light space-y-1">
                  <span className="text-[10px] uppercase font-bold text-vbc-gray block">ACO Identifier</span>
                  <span className="font-mono font-bold text-vbc-navy text-sm">{aco.id}</span>
                </div>

                <div className="p-3.5 bg-gray-50 rounded-lg border border-vbc-gray-light space-y-1">
                  <span className="text-[10px] uppercase font-bold text-vbc-gray block">ACO Name</span>
                  <span className="font-bold text-vbc-navy text-sm">{aco.name}</span>
                </div>

                <div className="p-3.5 bg-gray-50 rounded-lg border border-vbc-gray-light space-y-1">
                  <span className="text-[10px] uppercase font-bold text-vbc-gray block">Performance Year</span>
                  <span className="font-bold text-vbc-blue text-sm">PY {effectiveYear}</span>
                </div>

                <div className="p-3.5 bg-gray-50 rounded-lg border border-vbc-gray-light space-y-1">
                  <span className="text-[10px] uppercase font-bold text-vbc-gray block">Agreement / MSSP Track</span>
                  <span className="font-bold text-vbc-navy">{aco.track || 'MSSP Track 1+'}</span>
                </div>

                <div className="p-3.5 bg-gray-50 rounded-lg border border-vbc-gray-light space-y-1">
                  <span className="text-[10px] uppercase font-bold text-vbc-gray block">Risk Model</span>
                  <span className="font-bold text-vbc-navy">{aco.riskModel || 'Two-Sided Risk'}</span>
                </div>

                <div className="p-3.5 bg-gray-50 rounded-lg border border-vbc-gray-light space-y-1">
                  <span className="text-[10px] uppercase font-bold text-vbc-gray block">Benchmark Calculation Method</span>
                  <span className="font-bold text-vbc-navy">{aco.benchmarkMethod || 'CMS Regional Historical'}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: CLINICIAN PANEL METRICS */}
        {activeTab === 'providers' && (
          <ProviderVariationChart providers={providers} acoName={aco.name} />
        )}

        {/* TAB 3: MEMBER POPULATION RISK */}
        {activeTab === 'members' && memberRisk && (
          <MemberRiskChart memberRisk={memberRisk} acoName={aco.name} />
        )}
      </div>
    </Layout>
  );
};

export default ACODetail;
