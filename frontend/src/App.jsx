import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { StatsProvider } from './context/StatsContext';
import Logo from './components/Logo';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import HomePage from './pages/HomePage';
import MatchDetailPage from './pages/MatchDetailPage';
import MyAnalysesPage from './pages/MyAnalysesPage';
import ProfilePage from './pages/ProfilePage';
import PremiumPage from './pages/PremiumPage';
import PaymentConfirmation from './pages/PaymentConfirmation';

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
  
  return children;
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
  
  return user ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <Router>
      <ThemeProvider>
        <AuthProvider>
          <StatsProvider>
            <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          <Route
            path="/"
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
          
          <Route path="*" element={<Navigate to="/" />} />
          </Routes>
          </StatsProvider>
        </AuthProvider>
      </ThemeProvider>
    </Router>
  );
}

export default App;
