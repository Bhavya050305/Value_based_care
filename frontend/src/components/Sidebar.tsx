import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  Search,
  Users,
  Compass,
  Bell,
  Target,
  LogOut,
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  FileBarChart,
  Sparkles
} from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
  onLogout: () => void;
  mobileOpen: boolean;
  setMobileOpen: (open: boolean) => void;
}

// Final sidebar per spec §2 — exact order and naming.
const menuItems = [
  { label: 'Portfolio Overview', path: '/dashboard', icon: <LayoutDashboard size={18} /> },
  // { label: 'Peer Target Finder', path: '/peer-target-finder', icon: <Target size={18} /> },
  { label: 'ACO Explorer', path: '/explorer', icon: <Search size={18} /> },
  { label: 'Provider Performance', path: '/providers', icon: <Users size={18} /> },
  { label: 'Member Attribution', path: '/members', icon: <Compass size={18} /> },
  { label: 'Alerts & Attention', path: '/alerts', icon: <Bell size={18} /> },
  { label: 'Forecast', path: '/forecast', icon: <TrendingUp size={18} /> },
  { label: 'Reports', path: '/reports', icon: <FileBarChart size={18} /> },
  { label: 'AI Assistant', path: '/ai-assistant', icon: <Sparkles size={18} /> }
];

export const Sidebar: React.FC<SidebarProps> = ({
  collapsed,
  setCollapsed,
  onLogout,
  mobileOpen,
  setMobileOpen
}) => {
  const { user } = useAuth();
  const initials = (user?.name || 'Demo User')
    .split(' ')
    .map((p) => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  return (
    <>
      {mobileOpen && (
        <div
          onClick={() => setMobileOpen(false)}
          className="lg:hidden fixed inset-0 bg-vbc-navy/40 backdrop-blur-sm z-30 transition-opacity"
        ></div>
      )}

      <aside
        className={`fixed top-0 bottom-0 left-0 bg-vbc-navy text-white flex flex-col justify-between z-40 transition-all duration-300 border-r border-vbc-navy-light/10 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        } ${collapsed ? 'w-16' : 'w-64'}`}
      >
        <div>
          <div className="h-16 flex items-center justify-between px-4 border-b border-vbc-navy-light/20 bg-vbc-navy-dark">
            <div className="flex items-center space-x-2.5 overflow-hidden">
              <div className="p-2 bg-vbc-blue rounded-lg text-white font-bold flex-shrink-0 flex items-center justify-center">
                IQ
              </div>
              {!collapsed && (
                <div className="font-extrabold text-sm tracking-wider uppercase whitespace-nowrap">
                  VBC Command<span className="text-vbc-blue-medium">IQ</span>
                </div>
              )}
            </div>

            <button
              onClick={() => setCollapsed(!collapsed)}
              className="hidden lg:flex p-1 hover:bg-vbc-navy-light/40 rounded transition-colors text-vbc-gray-light"
            >
              {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
            </button>
          </div>

          <nav className="p-3 space-y-1.5 overflow-y-auto max-h-[calc(100vh-170px)]">
            {menuItems.map((item, idx) => (
              <NavLink
                key={idx}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                    isActive
                      ? 'bg-vbc-blue text-white shadow-sm'
                      : 'text-vbc-gray-light hover:bg-vbc-navy-light/35 hover:text-white'
                  }`
                }
                onClick={() => setMobileOpen(false)}
              >
                <div className="flex-shrink-0">{item.icon}</div>
                {!collapsed && <span className="truncate">{item.label}</span>}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="p-3 space-y-1 bg-vbc-navy-dark/45 border-t border-vbc-navy-light/10">
          {!collapsed && (
            <div className="px-3 py-2 text-[10px] text-vbc-gray font-bold uppercase tracking-widest leading-relaxed">
              Enterprise Account
            </div>
          )}

          <div className="flex items-center space-x-3 px-3 py-2 rounded-lg text-xs">
            <div className="w-8 h-8 rounded-full bg-vbc-blue-light text-vbc-blue font-bold flex items-center justify-center flex-shrink-0">
              {initials}
            </div>
            {!collapsed && (
              <div className="overflow-hidden">
                <div className="font-bold text-white truncate text-xs leading-none">{user?.name || 'Demo User'}</div>
                <span className="text-[10px] text-vbc-gray truncate mt-1 block">{user?.email || 'demo@vbccommandiq.com'}</span>
              </div>
            )}
          </div>

          <button
            onClick={onLogout}
            className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold text-vbc-red hover:bg-vbc-red-light/10 transition-all text-left"
          >
            <div className="flex-shrink-0">
              <LogOut size={18} />
            </div>
            {!collapsed && <span>Logout Session</span>}
          </button>
        </div>
      </aside>
    </>
  );
};
export default Sidebar;
