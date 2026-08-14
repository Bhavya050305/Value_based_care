import { create } from 'zustand';

interface SelectionState {
  selectedNpi: string | null;
  selectedAcoId: string | null;
  setSelectedNpi: (npi: string | null) => void;
  setSelectedAcoId: (acoId: string | null) => void;
}

export const useSelectionStore = create<SelectionState>((set) => ({
  selectedNpi: null,
  selectedAcoId: null,
  setSelectedNpi: (npi) => set({ selectedNpi: npi }),
  setSelectedAcoId: (acoId) => set({ selectedAcoId: acoId }),
}));
