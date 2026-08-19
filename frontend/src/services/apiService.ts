import { ApiResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const TOKEN_KEY = 'vbc_token';

export const apiService = {
  getToken(): string {
    return localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY) || 'dev_demo_token';
  },


  setToken(token: string, remember: boolean = true) {
    if (remember) {
      localStorage.setItem(TOKEN_KEY, token);
    } else {
      sessionStorage.setItem(TOKEN_KEY, token);
    }
  },

  clearToken() {
    localStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(TOKEN_KEY);
  },

  /**
   * Performs standardized HTTP requests to the FastAPI backend.
   */
  async request<T>(
    endpoint: string,
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
    body?: any
  ): Promise<ApiResponse<T>> {
    try {
      const token = this.getToken();
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const json = await response.json();
      
      return {
        success: true,
        data: json.data !== undefined ? json.data : json,
        source: 'api',
        timestamp: new Date().toISOString(),
      };
    } catch (error: any) {
      console.warn(`[apiService] Request failed for ${endpoint}:`, error?.message || error);
      return {
        success: false,
        data: null as any,
        source: 'api',
        timestamp: new Date().toISOString(),
      };
    }
  }
};

