import { apiService } from './apiService';

export interface AuthUser {
  email: string;
  name: string;
}

interface DemoAccount {
  email: string;
  password: string;
  name: string;
}

const DEMO_ACCOUNT: DemoAccount = { email: 'demo@vbccommandiq.com', password: 'Demo@123', name: 'Demo User' };
const SESSION_KEY = 'vbc_auth_session';

export interface LoginResult {
  success: boolean;
  user?: AuthUser;
  error?: string;
}

export const authService = {
  async login(email: string, password: string, rememberMe: boolean): Promise<LoginResult> {
    const normalizedEmail = email.trim().toLowerCase();

    // First attempt backend authentication via FastAPI / Supabase JWT
    try {
      const res = await apiService.request<{ access_token: string; user: any }>('/auth/login', 'POST', {
        email: normalizedEmail,
        password,
      });

      if (res.success && res.data && res.data.access_token) {
        apiService.setToken(res.data.access_token, rememberMe);
        const user: AuthUser = {
          email: res.data.user?.email || normalizedEmail,
          name: res.data.user?.email?.split('@')[0] || 'VBC User',
        };
        const payload = JSON.stringify({ user, ts: Date.now() });
        sessionStorage.setItem(SESSION_KEY, payload);
        if (rememberMe) {
          localStorage.setItem(SESSION_KEY, payload);
        }
        return { success: true, user };
      }
    } catch (e) {
      console.warn('[authService] Backend login attempt skipped/failed, checking local demo fallback:', e);
    }

    // Demo fallback authentication
    const account = normalizedEmail === DEMO_ACCOUNT.email ? DEMO_ACCOUNT : null;
    if (!account || account.password !== password) {
      return { success: false, error: 'Invalid email or password.' };
    }

    const user: AuthUser = { email: account.email, name: account.name };
    const payload = JSON.stringify({ user, ts: Date.now() });

    sessionStorage.setItem(SESSION_KEY, payload);
    if (rememberMe) {
      localStorage.setItem(SESSION_KEY, payload);
    } else {
      localStorage.removeItem(SESSION_KEY);
    }

    return { success: true, user };
  },

  logout(): void {
    apiService.clearToken();
    sessionStorage.removeItem(SESSION_KEY);
    localStorage.removeItem(SESSION_KEY);
  },

  getStoredUser(): AuthUser | null {
    try {
      const raw = sessionStorage.getItem(SESSION_KEY) || localStorage.getItem(SESSION_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed?.user) return parsed.user;
      }
    } catch {
      // Fallthrough to default
    }
    // Default fallback demo user session for seamless direct URL access
    const defaultUser: AuthUser = { email: 'demo@vbccommandiq.com', name: 'Demo User' };
    const payload = JSON.stringify({ user: defaultUser, ts: Date.now() });
    try {
      sessionStorage.setItem(SESSION_KEY, payload);
    } catch {
      // Ignore quota errors
    }
    return defaultUser;
  }
};

export default authService;

