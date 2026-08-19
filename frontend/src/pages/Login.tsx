import React, { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { KeyRound, Mail, Activity, AlertCircle, Eye, EyeOff } from 'lucide-react';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export const Login: React.FC = () => {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const validate = (): boolean => {
    const errs: { email?: string; password?: string } = {};
    if (!email.trim()) errs.email = 'Email is required.';
    else if (!EMAIL_RE.test(email.trim())) errs.email = 'Enter a valid email address.';
    if (!password) errs.password = 'Password is required.';
    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!validate()) return;

    setLoading(true);
    // DEMO AUTH ONLY — REPLACE WITH SUPABASE AUTH
    const result = await login(email, password, rememberMe);
    setLoading(false);

    if (result.success) {
      navigate('/dashboard', { replace: true });
    } else {
      setError(result.error || 'Invalid credentials.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl border border-vbc-gray-light shadow-2xl w-full max-w-md overflow-hidden grid grid-cols-1">
        <div className="bg-vbc-navy p-8 text-center text-white space-y-3 relative overflow-hidden">
          <div className="absolute right-0 top-0 w-32 h-32 bg-vbc-blue rounded-full blur-2xl opacity-20 pointer-events-none"></div>
          <div className="inline-flex p-3 bg-vbc-blue rounded-xl text-white mx-auto shadow-sm">
            <Activity size={24} />
          </div>
          <div>
            <h1 className="text-xl font-extrabold tracking-wide uppercase">
              VBC Command<span className="text-vbc-blue-medium">IQ</span>
            </h1>
            <p className="text-xs text-vbc-gray-light font-semibold tracking-wider uppercase mt-1">
              Value-Based Care Contract Performance Command Center
            </p>
          </div>
        </div>

        <div className="p-8 space-y-6">
          {error && (
            <div className="bg-vbc-red-light border border-vbc-red/20 text-vbc-red-dark text-xs p-3 rounded-lg flex items-start space-x-2">
              <AlertCircle size={15} className="flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4" noValidate>
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-vbc-navy block">Email Address</label>
              <div className="relative">
                <Mail size={16} className="absolute left-3 top-2.5 text-vbc-gray" />
                <input
                  type="email"
                  placeholder="name@vbccommandiq.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={`w-full bg-gray-50 border hover:border-vbc-gray focus:border-vbc-blue focus:outline-none pl-10 pr-4 py-2 rounded-lg text-xs ${
                    fieldErrors.email ? 'border-vbc-red' : 'border-vbc-gray-light'
                  }`}
                />
              </div>
              {fieldErrors.email && <span className="text-[10px] text-vbc-red-dark font-semibold">{fieldErrors.email}</span>}
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-vbc-navy block">Password</label>
              <div className="relative">
                <KeyRound size={16} className="absolute left-3 top-2.5 text-vbc-gray" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={`w-full bg-gray-50 border hover:border-vbc-gray focus:border-vbc-blue focus:outline-none pl-10 pr-10 py-2 rounded-lg text-xs ${
                    fieldErrors.password ? 'border-vbc-red' : 'border-vbc-gray-light'
                  }`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((s) => !s)}
                  className="absolute right-3 top-2 text-vbc-gray hover:text-vbc-navy"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
              {fieldErrors.password && <span className="text-[10px] text-vbc-red-dark font-semibold">{fieldErrors.password}</span>}
            </div>

            <div className="flex items-center justify-between text-xs">
              <label className="flex items-center space-x-2 text-vbc-navy font-medium cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-3.5 h-3.5 rounded border-vbc-gray text-vbc-blue focus:ring-0"
                />
                <span>Remember me</span>
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-vbc-blue hover:bg-vbc-blue-medium disabled:opacity-40 text-white font-semibold py-2.5 rounded-lg text-xs transition-opacity shadow-sm"
            >
              {loading ? 'Authenticating...' : 'Sign In'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
export default Login;
