import { useAuth } from '../context/AuthContext';
import { Bell, Star } from 'lucide-react';
import Logo from './Logo';

export default function Header({ title, subtitle, showLogo = false }) {
  const { user } = useAuth();

  return (
    <header className="bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 text-white px-4 pt-safe">
      <div className="max-w-lg mx-auto">
        {/* User Info */}
        <div className="flex items-center justify-between py-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center text-xl font-bold border border-white/30">
              {user?.username?.charAt(0).toUpperCase()}
            </div>
            <div>
              <p className="text-sm text-primary-100">Olá,</p>
              <p className="font-bold text-lg">{user?.username}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {user?.is_premium && (
              <div className="bg-yellow-400/20 backdrop-blur-sm px-3 py-1.5 rounded-full flex items-center gap-1.5 border border-yellow-300/40">
                <Star className="w-4 h-4 text-yellow-300 fill-yellow-300" />
                <span className="text-xs font-semibold text-yellow-100">Premium</span>
              </div>
            )}
            <button className="w-10 h-10 bg-white/15 backdrop-blur-sm rounded-xl flex items-center justify-center hover:bg-white/25 transition-all border border-white/30">
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
            <h1 className="text-3xl font-bold mb-1">{title}</h1>
            {subtitle && (
              <p className="text-primary-100 text-sm">{subtitle}</p>
            )}
          </div>
        ) : null}
      </div>
    </header>
  );
}
