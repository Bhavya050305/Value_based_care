import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Building2,
  Users,
  BarChart3,
  TrendingUp,
  HeartPulse,
  Award,
  AlertTriangle,
  Sliders,
  Sparkles,
  CheckSquare,
  Bot,
  X,
} from 'lucide-react';
import { usePreferenceStore } from '../../store/preferenceStore';

interface NavItem {
  name: string;
  path: string;
  icon: any;
  badge?: string;
  badgeColor?: string;
}

export const Sidebar: React.FC = () => {
  const { sidebarOpen, setSidebarOpen } = usePreferenceStore();

  const navItems: NavItem[] = [
    { name: 'Overview', path: '/overview', icon: LayoutDashboard },
    { name: 'ACO Explorer', path: '/acos', icon: Building2 },
    { name: 'Provider Explorer', path: '/providers', icon: Users },
    { name: 'Performance', path: '/performance', icon: BarChart3 },
    { name: 'Cost & Utilization', path: '/utilization', icon: TrendingUp },
    { name: 'Beneficiary Profile', path: '/beneficiaries', icon: HeartPulse },
    { name: 'Quality & Outcomes', path: '/quality', icon: Award },
    { name: 'Alerts & Attention', path: '/alerts', icon: AlertTriangle, badge: '5', badgeColor: 'bg-rose-500/20 text-rose-300 border-rose-800' },
    { name: 'What-If Simulator', path: '/simulator', icon: Sliders },
    { name: 'AI Insights', path: '/insights', icon: Sparkles, badge: 'Demo', badgeColor: 'bg-blue-500/20 text-blue-300 border-blue-800' },
    { name: 'Recommendations', path: '/recommendations', icon: CheckSquare, badge: '4', badgeColor: 'bg-emerald-500/20 text-emerald-300 border-emerald-800' },
    { name: 'AI Assistant', path: '/assistant', icon: Bot, badge: 'Chat', badgeColor: 'bg-purple-500/20 text-purple-300 border-purple-800' },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-xs lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed lg:static top-0 left-0 z-50 h-full w-64 bg-slate-950 border-r border-slate-800/80 flex flex-col transition-transform duration-300 ease-in-out font-sans ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Mobile Header Close */}
        <div className="p-4 flex items-center justify-between border-b border-slate-800/80 lg:hidden">
          <span className="text-xs font-bold text-slate-300 tracking-wider">COMMAND CENTER</span>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Sidebar Nav Items */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          <div className="px-3 pb-2 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
            COMMAND CENTER
          </div>

          {navItems.slice(0, 7).map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-blue-600/15 text-blue-400 font-semibold border border-blue-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{item.name}</span>
                </div>
              </NavLink>
            );
          })}

          <div className="pt-4 px-3 pb-2 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
            INTELLIGENCE & ACTION
          </div>

          {navItems.slice(7).map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-blue-600/15 text-blue-400 font-semibold border border-blue-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className={`px-1.5 py-0.5 text-[10px] font-mono rounded border ${item.badgeColor}`}>
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </div>

        {/* Sidebar Footer info */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-950/80">
          <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800 text-[11px] text-slate-400 space-y-1">
            <div className="flex justify-between items-center text-slate-300 font-medium">
              <span>CMS Dataset V24.1</span>
              <span className="text-[10px] font-mono px-1 bg-slate-800 text-blue-300 rounded">Phase 1</span>
            </div>
            <p className="text-[10px] text-slate-500 leading-tight">
              Value-Based Care Contract Engine with Backend Service Adapter pattern.
            </p>
          </div>
        </div>
      </aside>
    </>
  );
};
