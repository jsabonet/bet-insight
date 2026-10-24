import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { StatsProvider } from './context/StatsContext';
import { StrategyProvider } from './context/StrategyContext';
import Logo from './components/Logo';
import ScrollToTop from './components/ScrollToTop';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import HomePage from './pages/HomePage';
import MatchDetailPage from './pages/MatchDetailPage';
import MyAnalysesPage from './pages/MyAnalysesPage';
import ProfilePage from './pages/ProfilePage';
import PremiumPage from './pages/PremiumPage';
import AffiliateDashboardPage from './pages/AffiliateDashboardPage';
import AffiliateApplyPage from './pages/AffiliateApplyPage';
import PaymentConfirmation from './pages/PaymentConfirmation';
import TermsPage from './pages/TermsPage';
import PrivacyPage from './pages/PrivacyPage';
import AboutPage from './pages/AboutPage';
import FAQPage from './pages/FAQPage';
import DailyBetsPage from './pages/DailyBetsPage';
import CookieConsent from './components/CookieConsent';
import PushNotificationPrompt from './components/PushNotificationPrompt';
import TestQuickAnalyze from './pages/TestQuickAnalyze.jsx';

import AdminDashboard from './pages/admin/AdminDashboard';
import AdminUsers from './pages/admin/AdminUsers';
import AdminDailyBets from './pages/admin/AdminDailyBets';
import AdminExecutionDetail from './pages/admin/AdminExecutionDetail';
import AdminSocialProof from './pages/admin/AdminSocialProof';
import AdminAffiliates from './pages/admin/AdminAffiliates';

import { captureAffiliateRef } from './utils/affiliate';

// Captura o código de afiliado (?ref=CODE) ao carregar a app.
captureAffiliateRef();

// AdminRoute component - Staff e superusuários
function AdminRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <Logo variant="thinking" size="xl" showText={false} />
      </div>
    );
  }
  
  if (!user) return <Navigate to="/login" />;
  if (!user.is_staff && !user.is_superuser) return <Navigate to="/" />;
  
  return (
    <>
      <CookieConsent />
      {children}
    </>
  );
}

// ProtectedRoute component
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <Logo variant="thinking" size="xl" showText={false} />
      </div>
    );
  }
  
  return user ? (
    <>
      <CookieConsent />
      <PushNotificationPrompt />
      {children}
    </>
  ) : (
    <Navigate to="/landing" />
  );
}

// Após o checkout hospedado da VPay, o utilizador regressa ao site sem a
// referência da transação na URL. Este componente lê a transação guardada em
// sessionStorage e encaminha para a página de confirmação (polling).
function VPayReturnHandler() {
  const navigate = useNavigate();

  useEffect(() => {
    const pending = sessionStorage.getItem('vpay_pending_transaction');
    if (pending) {
      sessionStorage.removeItem('vpay_pending_transaction');
      navigate(`/payment/confirmation/${pending}`, { replace: true });
    }
  }, [navigate]);

  return null;
}

// PublicRoute - redirects authenticated users to home
function PublicRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <Logo variant="thinking" size="xl" showText={false} />
      </div>
    );
  }
  
  return !user ? children : <Navigate to="/home" />;
}

function App() {
  return (
    <HelmetProvider>
      <Router>
        <ScrollToTop />
        <VPayReturnHandler />
        <ThemeProvider>
        <AuthProvider>
          <StatsProvider>            <StrategyProvider>            <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Navigate to="/landing" replace />} />
          <Route
            path="/landing"
            element={
              <PublicRoute>
                <LandingPage />
              </PublicRoute>
            }
          />
          <Route
            path="/login"
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            }
          />
          <Route
            path="/register"
            element={
              <PublicRoute>
                <RegisterPage />
              </PublicRoute>
            }
          />
          
          {/* Legal Pages - accessible to everyone */}
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/faq" element={<FAQPage />} />
          {/* Public test route for quick analyze */}
          <Route path="/test/quick-analyze" element={<TestQuickAnalyze />} />
          
          {/* Protected Routes */}
          <Route
            path="/home"
            element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/daily-bets"
            element={
              <ProtectedRoute>
                <DailyBetsPage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/match/:id"
            element={
              <ProtectedRoute>
                <MatchDetailPage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/my-analyses"
            element={
              <ProtectedRoute>
                <MyAnalysesPage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/premium"
            element={
              <ProtectedRoute>
                <PremiumPage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/affiliate"
            element={
              <ProtectedRoute>
                <AffiliateDashboardPage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/affiliate/apply"
            element={
              <ProtectedRoute>
                <AffiliateApplyPage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/payment/confirmation/:transactionId"
            element={
              <ProtectedRoute>
                <PaymentConfirmation />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/admin"
            element={
              <AdminRoute>
                <AdminDashboard />
              </AdminRoute>
            }
          />
          
          <Route
            path="/admin/users"
            element={
              <AdminRoute>
                <AdminUsers />
              </AdminRoute>
            }
          />
          
          <Route
            path="/admin/daily-bets"
            element={
              <AdminRoute>
                <AdminDailyBets />
              </AdminRoute>
            }
          />
          
          <Route
            path="/admin/affiliates"
            element={
              <AdminRoute>
                <AdminAffiliates />
              </AdminRoute>
            }
          />
          
          <Route
            path="/admin/execution/:id"
            element={
              <AdminRoute>
                <AdminExecutionDetail />
              </AdminRoute>
            }
          />
          
          <Route
            path="/admin/social-proof"
            element={
              <AdminRoute>
                <AdminSocialProof />
              </AdminRoute>
            }
          />
          
          <Route path="*" element={<Navigate to="/landing" />} />
          </Routes>
            </StrategyProvider>
          </StatsProvider>
        </AuthProvider>
      </ThemeProvider>
    </Router>
    </HelmetProvider>
  );
}

export default App;
