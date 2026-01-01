import { NavLink } from 'react-router-dom';
import { Home, TrendingUp, Star, User, Shield } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function BottomNav() {
  const { user } = useAuth();

  const baseNavItems = [
    {
      path: '/',
      icon: Home,
      label: 'Início',
    },
    {
      path: '/my-analyses',
      icon: TrendingUp,
      label: 'Análises',
      badge: user?.analyses_count_today,
    },
    {
      path: '/premium',
      icon: Star,
      label: 'Premium',
      highlight: !user?.is_premium,
    },
    {
      path: '/profile',
      icon: User,
      label: 'Perfil',
    },
  ];

  // Adicionar item Admin para staff ou superusuários
  const navItems = (user?.is_staff || user?.is_superuser)
    ? [
        ...baseNavItems.slice(0, 3),
        {
          path: '/admin',
          icon: Shield,
          label: 'Admin',
          adminOnly: true,
        },
        ...baseNavItems.slice(3),
      ]
    : baseNavItems;

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white/95 dark:bg-gray-900/95 backdrop-blur-md border-t border-gray-200 dark:border-gray-700/50 z-50 safe-area-bottom shadow-2xl dark:shadow-black/50">
      <div className="max-w-lg mx-auto px-2">
        <div className="flex items-center justify-around py-2">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex flex-col items-center justify-center gap-1 px-4 py-2 rounded-xl transition-all relative ${
                  isActive
                    ? 'text-primary-600 dark:text-primary-400'
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <div className="relative">
                    <item.icon 
                      className={`w-6 h-6 transition-all ${
                        isActive ? 'scale-110' : ''
                      } ${item.highlight && !user?.is_premium ? 'text-yellow-500' : ''} ${item.adminOnly ? 'text-red-600 dark:text-red-400' : ''}`}
                      strokeWidth={isActive ? 2.5 : 2}
                    />
                    {item.badge > 0 && (
                      <span className="absolute -top-1 -right-1 bg-primary-600 text-white text-xs font-bold rounded-full w-4 h-4 flex items-center justify-center">
                        {item.badge}
                      </span>
                    )}
                    {item.highlight && !user?.is_premium && (
                      <span className="absolute -top-1 -right-1 w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></span>
                    )}
                  </div>
                  <span className={`text-xs font-medium ${isActive ? 'font-semibold' : ''}`}>
                    {item.label}
                  </span>
                  {isActive && (
                    <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-12 h-1 bg-primary-600 rounded-t-full"></div>
                  )}
                </>
              )}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  );
}
