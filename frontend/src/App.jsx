import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { StatsProvider } from './context/StatsContext';
import Logo from './components/Logo';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import HomePage from './pages/HomePage';
import MatchDetailPage from './pages/MatchDetailPage';
import MyAnalysesPage from './pages/MyAnalysesPage';
import ProfilePage from './pages/ProfilePage';
import PremiumPage from './pages/PremiumPage';
import PaymentConfirmation from './pages/PaymentConfirmation';
import TermsPage from './pages/TermsPage';
import PrivacyPage from './pages/PrivacyPage';
import AboutPage from './pages/AboutPage';
import CookieConsent from './components/CookieConsent';

import AdminDashboard from './pages/admin/AdminDashboard';
import AdminUsers from './pages/admin/AdminUsers';

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
      {children}
    </>
  ) : (
    <Navigate to="/landing" />
  );
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
    <Router>
      <ThemeProvider>
        <AuthProvider>
          <StatsProvider>
            <Routes>
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
          
          <Route path="*" element={<Navigate to="/landing" />} />
          </Routes>
          </StatsProvider>
        </AuthProvider>
      </ThemeProvider>
    </Router>
  );
}

export default App;
