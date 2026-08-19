import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { DataModeProvider } from './context/DataModeContext';
import { ACOProvider } from './context/ACOContext';
import { AIContextProvider } from './context/AIContextContext';
import { ProtectedRoute } from './components/ProtectedRoute';

import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { ACOExplorerPage } from './pages/ACOExplorerPage';
import { ACODetail } from './pages/ACODetail';
import { ProviderPerformancePage } from './pages/ProviderPerformancePage';
import { MemberAttributionPage } from './pages/MemberAttributionPage';
import { AlertsPage } from './pages/AlertsPage';
import { PeerTargetFinderPage } from './pages/PeerTargetFinderPage';
import { ForecastPage } from './pages/ForecastPage';
import { ReportsPage } from './pages/ReportsPage';
import { AIAssistantPage } from './pages/AIAssistantPage';

function App() {
  return (
    <AuthProvider>
      <DataModeProvider>
        <ACOProvider>
          <AIContextProvider>
            <BrowserRouter>
              <Routes>
                <Route path="/login" element={<Login />} />

                <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                <Route path="/explorer" element={<ProtectedRoute><ACOExplorerPage /></ProtectedRoute>} />
                <Route path="/aco/:acoId" element={<ProtectedRoute><ACODetail /></ProtectedRoute>} />
                <Route path="/providers" element={<ProtectedRoute><ProviderPerformancePage /></ProtectedRoute>} />
                <Route path="/members" element={<ProtectedRoute><MemberAttributionPage /></ProtectedRoute>} />
                <Route path="/alerts" element={<ProtectedRoute><AlertsPage /></ProtectedRoute>} />
                <Route path="/peer-target-finder" element={<ProtectedRoute><PeerTargetFinderPage /></ProtectedRoute>} />
                <Route path="/forecast" element={<ProtectedRoute><ForecastPage /></ProtectedRoute>} />
                <Route path="/reports" element={<ProtectedRoute><ReportsPage /></ProtectedRoute>} />
                <Route path="/ai-assistant" element={<ProtectedRoute><AIAssistantPage /></ProtectedRoute>} />

                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </BrowserRouter>
          </AIContextProvider>
        </ACOProvider>
      </DataModeProvider>
    </AuthProvider>

  );
}

export default App;
