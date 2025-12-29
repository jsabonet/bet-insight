import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Bell, Star, Sun, Moon } from 'lucide-react';
import Logo from './Logo';
import UserAvatar from './UserAvatar';

export default function Header({ title, subtitle, showLogo = false }) {
  const { user } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 text-white px-4 pt-safe border-b border-transparent dark:border-gray-700/50">
      <div className="max-w-lg mx-auto">
        {/* User Info */}
        <div className="flex items-center justify-between py-4">
          <div className="flex items-center gap-3">
            <UserAvatar user={user} size="md" showBadge={true} />
            <div>
              <p className="text-sm text-primary-100 dark:text-gray-400">Olá,</p>
              <p className="font-bold text-lg text-white dark:text-gray-100">{user?.username}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {user?.is_premium && (
              <div className="bg-yellow-400/20 dark:bg-yellow-500/20 backdrop-blur-sm px-3 py-1.5 rounded-full flex items-center gap-1.5 border border-yellow-300/40 dark:border-yellow-400/40">
                <Star className="w-4 h-4 text-yellow-300 dark:text-yellow-400 fill-yellow-300 dark:fill-yellow-400" />
                <span className="text-xs font-semibold text-yellow-100 dark:text-yellow-300">Premium</span>
              </div>
            )}
            <button 
              onClick={toggleTheme}
              className="w-10 h-10 bg-white/15 dark:bg-gray-700/50 backdrop-blur-sm rounded-xl flex items-center justify-center hover:bg-white/25 dark:hover:bg-gray-600/50 transition-all border border-white/30 dark:border-gray-600/50"
              aria-label="Alternar tema"
            >
              {theme === 'dark' ? (
                <Sun className="w-5 h-5 text-yellow-300" />
              ) : (
                <Moon className="w-5 h-5" />
              )}
            </button>
            <button className="w-10 h-10 bg-white/15 dark:bg-gray-700/50 backdrop-blur-sm rounded-xl flex items-center justify-center hover:bg-white/25 dark:hover:bg-gray-600/50 transition-all border border-white/30 dark:border-gray-600/50">
              <Bell className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Title or Logo */}
        {showLogo ? (
          <div className="pb-6">
            <Logo variant="default" size="md" showText={true} />
          </div>
        ) : title ? (
          <div className="pb-6">
            <h1 className="text-3xl font-bold mb-1 text-white dark:text-gray-100">{title}</h1>
            {subtitle && (
              <p className="text-primary-100 dark:text-gray-400 text-sm">{subtitle}</p>
            )}
          </div>
        ) : null}
      </div>
    </header>
  );
}
