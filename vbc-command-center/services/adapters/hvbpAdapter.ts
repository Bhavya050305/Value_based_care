import { HospitalRecord } from '../../types/hospital';

export function transformHVBPRecord(raw: any): HospitalRecord {
  const num = (v: any, fallback = 0) => {
    const parsed = Number(v);
    return isNaN(parsed) ? fallback : parsed;
  };

  const hai1Score = num(raw['HAI-1 Measure Score'], 8);
  const hai2Score = num(raw['HAI-2 Measure Score'], 9);
  const sep1Score = num(raw['SEP-1 Measure Score'], 8);
  const avgScore = (hai1Score + hai2Score + sep1Score) / 3;

  return {
    fiscalYear: String(raw['Fiscal Year'] || '2024'),
    facilityId: String(raw['Facility ID'] || '100001'),
    facilityName: String(raw['Facility Name'] || 'St. Jude Regional Medical Center'),
    state: String(raw['State'] || 'FL'),
    hai1PerformanceRate: num(raw['HAI-1 Performance Rate'], 0.42),
    hai1MeasureScore: hai1Score,
    hai2PerformanceRate: num(raw['HAI-2 Performance Rate'], 0.18),
    hai2MeasureScore: hai2Score,
    hai3PerformanceRate: num(raw['HAI-3 Performance Rate'], 0.55),
    hai3MeasureScore: num(raw['HAI-3 Measure Score'], 7),
    hai4PerformanceRate: num(raw['HAI-4 Performance Rate'], 0.38),
    hai4MeasureScore: num(raw['HAI-4 Measure Score'], 8),
    hai5PerformanceRate: num(raw['HAI-5 Performance Rate'], 0.04),
    hai5MeasureScore: num(raw['HAI-5 Measure Score'], 10),
    hai6PerformanceRate: num(raw['HAI-6 Performance Rate'], 0.62),
    hai6MeasureScore: num(raw['HAI-6 Measure Score'], 6),
    sep1PerformanceRate: num(raw['SEP-1 Performance Rate'], 84.5),
    sep1MeasureScore: sep1Score,
    overallQualityTier: avgScore >= 8.5 ? 'Top Decile' : avgScore >= 7.0 ? 'Above Average' : avgScore >= 5.5 ? 'Average' : 'Needs Improvement',
  };
}
