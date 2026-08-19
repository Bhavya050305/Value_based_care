import { apiService } from './apiService';

function triggerBlobDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export const reportService = {
  fullReportPages: [
    'Executive Summary',
    'Contract & ACO Profile',
    'Financial Performance',
    'Quality Performance',
    'Utilization Performance',
    'Population & Risk Profile',
    'Provider / Service Variation',
    'Performance Drivers',
    'ML Risk & Anomalies',
    'Peer Benchmark & Target Finder',
    'Recommendations & Action Analysis',
    'Provider Review Questions',
    'Technical / Data Appendix'
  ],

  /**
   * Triggers server-side ReportLab PDF report generation and download.
   */
  async downloadACOReport(acoId: string, year: number = 2024): Promise<void> {
    const endpoint = `/acos/${acoId}/pdf-report?year=${year}`;
    const filename = `ACO_${acoId}_Performance_Report_${year}.pdf`;

    try {
      const token = apiService.getToken();
      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`http://localhost:8000/api/v1${endpoint}`, {
        method: 'GET',
        headers,
      });

      if (!response.ok) {
        throw new Error(`Report generation failed with HTTP status ${response.status}`);
      }

      const blob = await response.blob();
      if (!blob || blob.size === 0) {
        throw new Error('Returned PDF blob is empty');
      }

      triggerBlobDownload(blob, filename);
    } catch (err: any) {
      console.error('Failed to download PDF report:', err);
      alert(`Unable to generate PDF report: ${err?.message || err}`);
    }
  }
};
