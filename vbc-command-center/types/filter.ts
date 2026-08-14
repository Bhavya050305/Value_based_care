export interface GlobalFilterState {
  year: string;
  state: string;
  providerType: string;
  riskLevel: string;
  performanceTier: string;
  beneficiaryVolume: string;
  searchQuery: string;

  setYear: (year: string) => void;
  setState: (state: string) => void;
  setProviderType: (providerType: string) => void;
  setRiskLevel: (riskLevel: string) => void;
  setPerformanceTier: (tier: string) => void;
  setBeneficiaryVolume: (volume: string) => void;
  setSearchQuery: (query: string) => void;
  resetFilters: () => void;
}
