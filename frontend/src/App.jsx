import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';

// Layouts
import LandingLayout from './layouts/LandingLayout';
import DashboardLayout from './layouts/DashboardLayout';

// Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import CompleteProfile from './pages/CompleteProfile';
import DataUpload from './pages/DataUpload';
import Dashboard from './pages/Dashboard';
import TalkToData from './pages/TalkToData';
import Forecasting from './pages/Forecasting';
import InvoiceRisk from './pages/InvoiceRisk';
import WorkingCapital from './pages/WorkingCapital';
import BankingRecommendation from './pages/BankingRecommendation';
import Settings from './pages/Settings';
import TeamWorkspace from './pages/TeamWorkspace';

// Bank Pages
import BankPortfolio from './pages/bank/BankPortfolio';
import HighRiskList from './pages/bank/HighRiskList';
import CustomerDetail from './pages/bank/CustomerDetail';
import RiskDefaultPrediction from './pages/bank/RiskDefaultPrediction';
import LendingOpportunities from './pages/bank/LendingOpportunities';
import Explainability from './pages/bank/Explainability';
import Alerts from './pages/bank/AlertsCenter';
import SystemAdmin from './pages/bank/SystemAdmin';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  return children;
};

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<LandingLayout />}>
              <Route index element={<LandingPage />} />
            </Route>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />

            {/* Protected Routes */}
            <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
              {/* MSME Routes */}
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/complete-profile" element={<CompleteProfile />} />
              <Route path="/upload-data" element={<DataUpload />} />
              <Route path="/forecast" element={<Forecasting />} />
              <Route path="/invoice-risk" element={<InvoiceRisk />} />
              <Route path="/working-capital" element={<WorkingCapital />} />
              <Route path="/banking-recommendations" element={<BankingRecommendation />} />
              <Route path="/talk-to-data" element={<TalkToData />} />
              
              {/* Bank Routes */}
              <Route path="/bank/portfolio" element={<BankPortfolio />} />
              <Route path="/bank/risk-list" element={<HighRiskList />} />
              <Route path="/bank/customer/:id" element={<CustomerDetail />} />
              <Route path="/bank/prediction" element={<RiskDefaultPrediction />} />
              <Route path="/bank/opportunities" element={<LendingOpportunities />} />
              <Route path="/bank/explainability" element={<Explainability />} />
              <Route path="/bank/alerts" element={<Alerts />} />
              <Route path="/bank/admin" element={<SystemAdmin />} />

              <Route path="/team" element={<TeamWorkspace />} />
              <Route path="/settings" element={<Settings />} />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
