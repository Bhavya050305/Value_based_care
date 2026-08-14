import { create } from 'zustand';
import { GlobalFilterState } from '../types/filter';

export const useFilterStore = create<GlobalFilterState>((set) => ({
  year: '2024',
  state: 'All',
  providerType: 'All',
  riskLevel: 'All',
  performanceTier: 'All',
  beneficiaryVolume: 'All',
  searchQuery: '',

  setYear: (year) => set({ year }),
  setState: (state) => set({ state }),
  setProviderType: (providerType) => set({ providerType }),
  setRiskLevel: (riskLevel) => set({ riskLevel }),
  setPerformanceTier: (performanceTier) => set({ performanceTier }),
  setBeneficiaryVolume: (beneficiaryVolume) => set({ beneficiaryVolume }),
  setSearchQuery: (searchQuery) => set({ searchQuery }),

  resetFilters: () =>
    set({
      year: '2024',
      state: 'All',
      providerType: 'All',
      riskLevel: 'All',
      performanceTier: 'All',
      beneficiaryVolume: 'All',
      searchQuery: '',
    }),
}));
