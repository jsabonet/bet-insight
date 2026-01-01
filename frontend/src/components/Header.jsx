import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useStats } from '../context/StatsContext';
import { Bell, Star, Sun, Moon } from 'lucide-react';
import Logo from './Logo';
import UserAvatar from './UserAvatar';
import DailyLimitIndicator from './DailyLimitIndicator';
import { authAPI } from '../services/api';
import InstallPWAButton from './InstallPWAButton';

export default function Header({ title, subtitle, showLogo = false }) {
  const { user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { refreshTrigger } = useStats();
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const res = await authAPI.getStats();
        setStats(res.data);
      } catch (e) {
        // ignore
      }
    };
    loadStats();
  }, []);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const res = await authAPI.getStats();
        setStats(res.data);
      } catch (e) {
        // ignore
      }
    };
    loadStats();
  }, [refreshTrigger]);

  return (
    <header className="bg-gradient-to-br from-primary-700 via-primary-800 to-primary-900 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 text-white px-4 pt-safe border-b border-transparent dark:border-gray-700/50">
      <div className="max-w-lg mx-auto">
        {/* User Info */}
        <div className="flex items-center justify-between py-4">
          <div className="flex items-center gap-3">
            <UserAvatar user={user} size="md" showBadge={true} isPremiumOverride={stats?.is_premium} />
            <div>
              <p className="text-sm text-primary-100 dark:text-gray-400">Olá,</p>
              <p className="font-bold text-lg text-white dark:text-gray-100">{user?.username}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <InstallPWAButton />
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
        
        {/* Daily Limit Indicator */}
        <div className="pb-3">
          <DailyLimitIndicator refreshTrigger={refreshTrigger} />
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
