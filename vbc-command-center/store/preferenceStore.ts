import { create } from 'zustand';

interface PreferenceState {
  sidebarOpen: boolean;
  searchModalOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setSearchModalOpen: (open: boolean) => void;
}

export const usePreferenceStore = create<PreferenceState>((set) => ({
  sidebarOpen: true,
  searchModalOpen: false,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setSearchModalOpen: (open) => set({ searchModalOpen: open }),
}));
