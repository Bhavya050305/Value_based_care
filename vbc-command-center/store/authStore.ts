import { create } from 'zustand';
import { AuthState, User } from '../types/auth';
import { loginUser, registerUser } from '../services/auth/authService';

const STORAGE_KEY = 'vbc_auth_session';

const getInitialUser = (): User | null => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (e) {
    console.error('Failed to parse auth session', e);
  }
  return null;
};

const initialUser = getInitialUser();

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: !!initialUser,
  user: initialUser,
  isLoading: false,
  error: null,

  signIn: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const user = await loginUser(email, password);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
      set({ isAuthenticated: true, user, isLoading: false, error: null });
      return true;
    } catch (err: any) {
      set({ error: err?.message || 'Authentication failed', isLoading: false });
      return false;
    }
  },

  signUp: async (data) => {
    set({ isLoading: true, error: null });
    try {
      await registerUser(data);
      set({ isLoading: false, error: null });
      return true;
    } catch (err: any) {
      set({ error: err?.message || 'Registration failed', isLoading: false });
      return false;
    }
  },

  signOut: () => {
    localStorage.removeItem(STORAGE_KEY);
    set({ isAuthenticated: false, user: null, error: null });
  },

  clearError: () => set({ error: null }),
}));
