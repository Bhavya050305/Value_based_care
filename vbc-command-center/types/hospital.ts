// Hospital Value-Based Purchasing (HVBP) Safety & Quality Data Model

export interface HospitalRecord {
  fiscalYear: string; // Fiscal Year
  facilityId: string; // Facility ID
  facilityName: string; // Facility Name
  state: string; // State

  // Healthcare-Associated Infections (HAI-1 to HAI-6)
  hai1PerformanceRate: number; // CAUTI (Catheter-Associated Urinary Tract Infections)
  hai1MeasureScore: number;
  hai2PerformanceRate: number; // CLABSI (Central Line-Associated Bloodstream Infections)
  hai2MeasureScore: number;
  hai3PerformanceRate: number; // SSI-Colon
  hai3MeasureScore: number;
  hai4PerformanceRate: number; // SSI-Abdominal Hysterectomy
  hai4MeasureScore: number;
  hai5PerformanceRate: number; // MRSA Bacteremia
  hai5MeasureScore: number;
  hai6PerformanceRate: number; // C. difficile
  hai6MeasureScore: number;

  // Clinical Care Protocol
  sep1PerformanceRate: number; // Severe Sepsis and Septic Shock Management
  sep1MeasureScore: number;

  overallQualityTier: 'Top Decile' | 'Above Average' | 'Average' | 'Needs Improvement';
}
