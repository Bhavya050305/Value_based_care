import React, { useState } from 'react';
import { useLocation, Link, useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  Search,
  Bell,
  Menu,
  ChevronRight,
  Calendar,
  Layers,
  Sparkles,
  User as UserIcon,
  LogOut,
  Settings,
  X,
  UserCheck,
} from 'lucide-react';
import { usePreferenceStore } from '../../store/preferenceStore';
import { useFilterStore } from '../../store/filterStore';
import { useAuthStore } from '../../store/authStore';
import { DataSourceBadge } from './DataSourceBadge';

export const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { toggleSidebar, setSearchModalOpen } = usePreferenceStore();
  const { year, setYear } = useFilterStore();
  const { user, signOut } = useAuthStore();

  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showSignOutDialog, setShowSignOutDialog] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);

  const getBreadcrumbName = (pathname: string) => {
    switch (pathname) {
      case '/':
      case '/overview':
        return 'Command Center Overview';
      case '/acos':
        return 'ACO Explorer';
      case '/providers':
        return 'Provider Explorer';
      case '/performance':
        return 'Performance Analytics';
      case '/utilization':
        return 'Cost & Utilization';
      case '/beneficiaries':
        return 'Beneficiary Profile';
      case '/quality':
        return 'Quality & Outcomes';
      case '/alerts':
        return 'Alerts & Attention';
      case '/simulator':
        return 'What-If Simulator';
      case '/insights':
        return 'AI Insights';
      case '/recommendations':
        return 'Recommendations';
      case '/assistant':
        return 'AI Assistant';
      default:
        if (pathname.startsWith('/providers/')) return 'Provider Detail';
        return 'Command Center Overview';
    }
  };

  const currentTitle = getBreadcrumbName(location.pathname);

  const handleConfirmSignOut = () => {
    setShowSignOutDialog(false);
    signOut();
    navigate('/login', { replace: true });
  };

  return (
    <>
      <header className="sticky top-0 z-40 bg-slate-950/90 backdrop-blur-md border-b border-slate-800/80 px-4 lg:px-6 py-3 flex items-center justify-between font-sans">
        {/* Left section: Mobile Hamburger & Title & Breadcrumb */}
        <div className="flex items-center gap-3">
          <button
            onClick={toggleSidebar}
            className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800/80 transition-colors lg:hidden"
            aria-label="Toggle Menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          <Link to="/overview" className="flex items-center gap-2 group">
            <div className="p-1.5 bg-blue-600 rounded-lg text-white shadow-lg shadow-blue-600/30 group-hover:bg-blue-500 transition-colors">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div className="hidden sm:block">
              <span className="font-bold text-xs sm:text-sm text-white tracking-tight block leading-tight">
                Value-Based Care Command Center
              </span>
              <span className="text-[10px] text-blue-400 font-medium tracking-wider block">
                PAYER PERFORMANCE & CONTRACT INTELLIGENCE
              </span>
            </div>
          </Link>

          <div className="hidden xl:flex items-center text-slate-500 text-xs ml-3 border-l border-slate-800 pl-3 gap-1.5">
            <Layers className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-400">Command Center</span>
            <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
            <span className="font-semibold text-slate-200">{currentTitle}</span>
          </div>
        </div>

        {/* Right Section: Global Controls, Year, Search, Notifications, User */}
        <div className="flex items-center gap-2.5">
          {/* Data Source Badge */}
          <DataSourceBadge />

          {/* Year Selector */}
          <div className="relative flex items-center bg-slate-900 border border-slate-800 rounded-lg px-2 py-1 text-xs">
            <Calendar className="w-3.5 h-3.5 text-blue-400 mr-1" />
            <select
              value={year}
              onChange={(e) => setYear(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer font-semibold text-xs"
            >
              <option value="2024" className="bg-slate-900 text-white">2024 PY</option>
              <option value="2023" className="bg-slate-900 text-white">2023 PY</option>
              <option value="2022" className="bg-slate-900 text-white">2022 PY</option>
            </select>
          </div>

          {/* Global Search Button */}
          <button
            onClick={() => setSearchModalOpen(true)}
            className="hidden md:flex items-center gap-2 bg-slate-900/80 hover:bg-slate-800 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-400 hover:text-white transition-colors"
          >
            <Search className="w-3.5 h-3.5 text-blue-400" />
            <span>Search NPI / Provider / ACO...</span>
            <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-[10px] text-slate-400 font-mono">Ctrl+K</kbd>
          </button>

          {/* Notifications Dropdown */}
          <div className="relative">
            <button
              onClick={() => {
                setShowNotifications(!showNotifications);
                setShowUserMenu(false);
              }}
              className="relative p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800/80 transition-colors"
              aria-label="Notifications"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full animate-ping" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full" />
            </button>

            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-4 z-50 animate-in fade-in zoom-in-95">
                <div className="flex justify-between items-center pb-2 border-b border-slate-800 mb-3">
                  <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-blue-400" /> Contract Alerts
                  </span>
                  <span className="text-[10px] px-1.5 py-0.5 bg-rose-950 text-rose-300 rounded border border-rose-800">3 New</span>
                </div>
                <div className="space-y-2.5 text-xs">
                  <div className="p-2 bg-slate-950/60 rounded border border-slate-800">
                    <span className="font-semibold text-rose-400 block">High Utilization Warning</span>
                    <span className="text-slate-400">Dr. Sarah Jenkins exceeds services/bene benchmark by +114%.</span>
                  </div>
                  <div className="p-2 bg-slate-950/60 rounded border border-slate-800">
                    <span className="font-semibold text-amber-400 block">ACO Benchmark Deficit</span>
                    <span className="text-slate-400">ACO-003 is tracking 2.1% below historical benchmark.</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* User Profile Section Header Dropdown */}
          <div className="relative border-l border-slate-800 pl-2.5 ml-1">
            <button
              onClick={() => {
                setShowUserMenu(!showUserMenu);
                setShowNotifications(false);
              }}
              className="flex items-center gap-2.5 p-1.5 rounded-xl hover:bg-slate-900 border border-transparent hover:border-slate-800 transition-colors"
            >
              <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/40 text-blue-400 flex items-center justify-center font-bold text-xs shrink-0">
                {user?.name ? user.name.split(' ').map((n) => n[0]).join('') : 'DK'}
              </div>
              <div className="hidden sm:block text-left">
                <div className="text-xs font-bold text-slate-200 leading-none">{user?.name || 'Divya K'}</div>
                <div className="text-[10px] text-slate-400 font-medium leading-tight mt-0.5">{user?.role || 'Payer Analyst'}</div>
              </div>
              <ChevronRight className={`w-3.5 h-3.5 text-slate-500 transition-transform ${showUserMenu ? 'rotate-90' : ''}`} />
            </button>

            {/* Dropdown Menu */}
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-56 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl py-2 z-50 animate-in fade-in zoom-in-95">
                <div className="px-3 py-2 border-b border-slate-800/80 mb-1">
                  <p className="text-xs font-bold text-white">{user?.name || 'Divya K'}</p>
                  <p className="text-[11px] text-slate-400 truncate">{user?.email || 'analyst@demo.com'}</p>
                  <span className="inline-block text-[10px] px-1.5 py-0.2 bg-blue-950 text-blue-300 rounded border border-blue-800 mt-1">
                    {user?.organization || 'Aetna Medicare Division'}
                  </span>
                </div>

                <button
                  onClick={() => {
                    setShowUserMenu(false);
                    setShowProfileModal(true);
                  }}
                  className="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 flex items-center gap-2"
                >
                  <UserCheck className="w-4 h-4 text-blue-400" />
                  <span>My Profile</span>
                </button>

                <button
                  onClick={() => {
                    setShowUserMenu(false);
                    alert('Settings & Preferences: Configured via Zustand stores.');
                  }}
                  className="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 flex items-center gap-2"
                >
                  <Settings className="w-4 h-4 text-slate-400" />
                  <span>Settings</span>
                </button>

                <div className="border-t border-slate-800/80 my-1" />

                <button
                  onClick={() => {
                    setShowUserMenu(false);
                    setShowSignOutDialog(true);
                  }}
                  className="w-full text-left px-3 py-2 text-xs text-rose-400 hover:bg-rose-950/40 flex items-center gap-2 font-medium"
                >
                  <LogOut className="w-4 h-4 text-rose-400" />
                  <span>Sign Out</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Sign Out Confirmation Dialog Modal */}
      {showSignOutDialog && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-sm w-full shadow-2xl space-y-4 animate-in fade-in zoom-in-95">
            <div className="flex items-center gap-3 text-rose-400">
              <div className="p-2.5 bg-rose-950/80 border border-rose-800 rounded-xl">
                <LogOut className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Sign out?</h3>
                <p className="text-xs text-slate-400">Are you sure you want to sign out of the Command Center?</p>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
              <button
                onClick={() => setShowSignOutDialog(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl transition"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmSignOut}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-rose-600/30 transition"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      )}

      {/* User Profile Modal */}
      {showProfileModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-slate-800">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <UserIcon className="w-4 h-4 text-blue-400" /> Analyst Profile
              </h3>
              <button
                onClick={() => setShowProfileModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 space-y-1">
                <div className="text-slate-400">Full Name</div>
                <div className="font-bold text-white text-sm">{user?.name || 'Divya K'}</div>
              </div>

              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 space-y-1">
                <div className="text-slate-400">Work Email</div>
                <div className="font-semibold text-slate-200">{user?.email || 'analyst@demo.com'}</div>
              </div>

              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 space-y-1">
                <div className="text-slate-400">Organization & Role</div>
                <div className="font-semibold text-blue-400">{user?.organization || 'Aetna Medicare Division'} — {user?.role || 'Payer Analyst'}</div>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => setShowProfileModal(false)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-xl"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
