import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { GlobalAIAssistant } from './GlobalAIAssistant';
import { useDataMode } from '../context/DataModeContext';
import { useAuth } from '../context/AuthContext';
import { reportService } from '../services/reportService';

interface LayoutProps {
  children: React.ReactNode;
  title: string;
  acoId?: string;
  acoName?: string;
  /** Optional override; Layout otherwise handles logout centrally via AuthContext. */
  onLogout?: () => void;
}

export const Layout: React.FC<LayoutProps> = ({
  children,
  title,
  acoId = 'abc-aco',
  acoName = 'ABC Health Partners ACO',
  onLogout
}) => {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { dataMode } = useDataMode();
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleDownloadReport = () => {
    reportService.downloadACOReport(acoId, 2024);
  };

  const handleLogout = () => {
    // Clear session -> update AuthContext -> navigate to /login
    logout();
    if (onLogout) onLogout();
    navigate('/login', { replace: true });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar
        collapsed={collapsed}
        setCollapsed={setCollapsed}
        onLogout={handleLogout}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
      />

      <div
        className={`flex-1 flex flex-col transition-all duration-300 min-h-screen ${
          collapsed ? 'lg:pl-16' : 'lg:pl-64'
        }`}
      >
        <Header
          title={title}
          onDownloadReport={handleDownloadReport}
          onMenuToggle={() => setMobileOpen(!mobileOpen)}
        />

        <main className={`flex-1 p-4 md:p-6 space-y-6 ${dataMode === 'connected' ? 'pt-14' : ''}`}>
          {children}
        </main>
      </div>

      {/* Single global contextual AI assistant, present on every authenticated page */}
      <GlobalAIAssistant />
    </div>
  );
};
export default Layout;
