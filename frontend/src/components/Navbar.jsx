import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, User, BarChart3, Home, CreditCard } from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center gap-2">
            <span className="text-2xl">⚽</span>
            <span className="text-xl font-bold text-primary-600">Bet Insight</span>
          </Link>

          <div className="flex items-center gap-4">
            <Link
              to="/"
              className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Home className="w-4 h-4" />
              <span className="hidden sm:inline">Partidas</span>
            </Link>

            <Link
              to="/my-analyses"
              className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <BarChart3 className="w-4 h-4" />
              <span className="hidden sm:inline">Minhas Análises</span>
            </Link>

            <Link
              to="/premium"
              className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <CreditCard className="w-4 h-4" />
              <span className="hidden sm:inline">Premium</span>
            </Link>

            <div className="flex items-center gap-3 pl-3 border-l border-gray-200">
              <Link
                to="/profile"
                className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <User className="w-4 h-4" />
                <span className="hidden sm:inline">{user?.username}</span>
              </Link>

              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-3 py-2 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Indicador Premium */}
      {user && (
        <div className="bg-gray-50 border-t border-gray-200 px-4 py-2">
          <div className="max-w-7xl mx-auto flex items-center justify-between text-sm">
            <div className="flex items-center gap-4">
              <span className="text-gray-600">
                Análises hoje: <strong>{user.daily_analysis_count}</strong> / {user.is_premium ? '100' : '5'}
              </span>
              {!user.is_premium && (
                <Link to="/premium" className="text-primary-600 hover:text-primary-700 font-medium">
                  Seja Premium →
                </Link>
              )}
            </div>
            {user.is_premium && (
              <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-medium">
                ⭐ PREMIUM
              </span>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
