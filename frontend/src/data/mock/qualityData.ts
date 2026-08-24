export interface QualityTrendPoint {
  year: number;
  qualityScore: number;
  preventiveCareRate: number;
  readmissionRate: number;
  patientExperience: number;
}

// DEMO DATA — Replace with Supabase/API response during final integration.
export const mockQualityByACO: Record<string, QualityTrendPoint[]> = {
  'abc-aco': [
    { year: 2021, qualityScore: 88.0, preventiveCareRate: 58.0, readmissionRate: 14.5, patientExperience: 82.0 },
    { year: 2022, qualityScore: 90.2, preventiveCareRate: 60.5, readmissionRate: 13.8, patientExperience: 84.5 },
    { year: 2023, qualityScore: 92.0, preventiveCareRate: 62.0, readmissionRate: 12.9, patientExperience: 87.0 },
    { year: 2024, qualityScore: 93.5, preventiveCareRate: 64.2, readmissionRate: 12.2, patientExperience: 89.5 },
    { year: 2025, qualityScore: 94.2, preventiveCareRate: 66.8, readmissionRate: 11.5, patientExperience: 91.0 }
  ],
  'xyz-aco': [
    { year: 2021, qualityScore: 82.0, preventiveCareRate: 51.0, readmissionRate: 16.2, patientExperience: 78.0 },
    { year: 2022, qualityScore: 83.5, preventiveCareRate: 53.0, readmissionRate: 15.8, patientExperience: 80.2 },
    { year: 2023, qualityScore: 84.8, preventiveCareRate: 55.4, readmissionRate: 15.1, patientExperience: 82.5 },
    { year: 2024, qualityScore: 85.9, preventiveCareRate: 57.0, readmissionRate: 14.6, patientExperience: 84.1 },
    { year: 2025, qualityScore: 86.5, preventiveCareRate: 59.2, readmissionRate: 14.0, patientExperience: 85.0 }
  ],
  'lmn-aco': [
    { year: 2021, qualityScore: 80.0, preventiveCareRate: 48.0, readmissionRate: 18.2, patientExperience: 74.0 },
    { year: 2022, qualityScore: 78.5, preventiveCareRate: 46.5, readmissionRate: 18.9, patientExperience: 73.1 },
    { year: 2023, qualityScore: 76.2, preventiveCareRate: 44.0, readmissionRate: 19.5, patientExperience: 71.8 },
    { year: 2024, qualityScore: 74.0, preventiveCareRate: 42.1, readmissionRate: 20.4, patientExperience: 70.2 },
    { year: 2025, qualityScore: 72.1, preventiveCareRate: 40.5, readmissionRate: 21.2, patientExperience: 69.0 }
  ],
  'pqr-aco': [
    { year: 2021, qualityScore: 84.0, preventiveCareRate: 54.0, readmissionRate: 15.8, patientExperience: 80.0 },
    { year: 2022, qualityScore: 83.2, preventiveCareRate: 55.0, readmissionRate: 16.1, patientExperience: 81.2 },
    { year: 2023, qualityScore: 82.8, preventiveCareRate: 55.8, readmissionRate: 16.3, patientExperience: 81.9 },
    { year: 2024, qualityScore: 82.5, preventiveCareRate: 56.2, readmissionRate: 16.6, patientExperience: 82.1 },
    { year: 2025, qualityScore: 82.4, preventiveCareRate: 56.5, readmissionRate: 16.8, patientExperience: 82.3 }
  ],
  'def-aco': [
    { year: 2021, qualityScore: 86.0, preventiveCareRate: 57.0, readmissionRate: 15.2, patientExperience: 81.0 },
    { year: 2022, qualityScore: 87.2, preventiveCareRate: 58.5, readmissionRate: 14.8, patientExperience: 83.0 },
    { year: 2023, qualityScore: 88.0, preventiveCareRate: 59.8, readmissionRate: 14.2, patientExperience: 84.8 },
    { year: 2024, qualityScore: 88.6, preventiveCareRate: 61.2, readmissionRate: 13.9, patientExperience: 86.0 },
    { year: 2025, qualityScore: 89.0, preventiveCareRate: 62.5, readmissionRate: 13.5, patientExperience: 87.2 }
  ],
  'ghi-aco': [
    { year: 2021, qualityScore: 83.0, preventiveCareRate: 52.0, readmissionRate: 17.5, patientExperience: 79.0 },
    { year: 2022, qualityScore: 81.5, preventiveCareRate: 50.8, readmissionRate: 18.2, patientExperience: 77.2 },
    { year: 2023, qualityScore: 80.2, preventiveCareRate: 49.5, readmissionRate: 18.9, patientExperience: 76.0 },
    { year: 2024, qualityScore: 79.1, preventiveCareRate: 48.0, readmissionRate: 19.4, patientExperience: 74.8 },
    { year: 2025, qualityScore: 78.6, preventiveCareRate: 47.2, readmissionRate: 19.8, patientExperience: 74.0 }
  ]
};

export const getQualityData = (acoId: string): QualityTrendPoint[] => {
  return mockQualityByACO[acoId] || mockQualityByACO['abc-aco'];
};
