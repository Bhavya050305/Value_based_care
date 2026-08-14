// TypeScript definitions for Auth & User Profile

export interface User {
  id: string;
  name: string;
  email: string;
  organization: string;
  role: string;
  avatar?: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  isLoading: boolean;
  error: string | null;
  signIn: (email: string, password: string) => Promise<boolean>;
  signUp: (data: { name: string; email: string; organization: string; password: string }) => Promise<boolean>;
  signOut: () => void;
  clearError: () => void;
}
