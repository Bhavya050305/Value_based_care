import React from 'react';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';
import { ProtectedRoute } from '../auth/ProtectedRoute';
import { LoginPage } from '../pages/Auth/LoginPage';
import { SignUpPage } from '../pages/Auth/SignUpPage';
import { CommandCenterOverview } from '../pages/Overview/CommandCenterOverview';
import { ACOExplorer } from '../pages/ACOExplorer/ACOExplorer';
import { ProviderExplorer } from '../pages/ProviderExplorer/ProviderExplorer';
import { ProviderDetail } from '../pages/ProviderDetail/ProviderDetail';
import { PerformanceAnalytics } from '../pages/Performance/PerformanceAnalytics';
import { CostUtilization } from '../pages/Utilization/CostUtilization';
import { BeneficiaryProfile } from '../pages/Beneficiaries/BeneficiaryProfile';
import { QualityOutcomes } from '../pages/Quality/QualityOutcomes';
import { AlertsAttention } from '../pages/Alerts/AlertsAttention';
import { WhatIfSimulator } from '../pages/Simulator/WhatIfSimulator';
import { AIInsights } from '../pages/Insights/AIInsights';
import { Recommendations } from '../pages/Recommendations/Recommendations';
import { AIAssistant } from '../pages/Assistant/AIAssistant';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/signup',
    element: <SignUpPage />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <MainLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <Navigate to="/overview" replace /> },
      { path: 'overview', element: <CommandCenterOverview /> },
      { path: 'acos', element: <ACOExplorer /> },
      { path: 'providers', element: <ProviderExplorer /> },
      { path: 'providers/:npi', element: <ProviderDetail /> },
      { path: 'performance', element: <PerformanceAnalytics /> },
      { path: 'utilization', element: <CostUtilization /> },
      { path: 'beneficiaries', element: <BeneficiaryProfile /> },
      { path: 'quality', element: <QualityOutcomes /> },
      { path: 'alerts', element: <AlertsAttention /> },
      { path: 'simulator', element: <WhatIfSimulator /> },
      { path: 'insights', element: <AIInsights /> },
      { path: 'recommendations', element: <Recommendations /> },
      { path: 'assistant', element: <AIAssistant /> },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/overview" replace />,
  },
]);

export const AppRouter: React.FC = () => {
  return <RouterProvider router={router} />;
};
