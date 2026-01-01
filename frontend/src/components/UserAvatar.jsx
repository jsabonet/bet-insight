import { User, Crown, Shield, Star } from 'lucide-react';

/**
 * UserAvatar - Avatar dinâmico baseado no tipo de usuário
 * @param {Object} user - Objeto do usuário
 * @param {String} size - Tamanho: 'sm', 'md', 'lg', 'xl'
 * @param {Boolean} showBadge - Mostrar badge de tipo
 */
export default function UserAvatar({ user, size = 'md', showBadge = false, isPremiumOverride = undefined }) {
  // Determinar tipo de usuário
  const getUserType = () => {
    if (user?.is_superuser) return 'superuser';
    if (user?.is_staff) return 'staff';
    if (typeof isPremiumOverride !== 'undefined') {
      return isPremiumOverride ? 'premium' : 'free';
    }
    if (user?.is_premium) return 'premium';
    return 'free';
  };

  const userType = getUserType();

  // Configurações de tamanho
  const sizes = {
    sm: {
      container: 'w-10 h-10',
      icon: 'w-5 h-5',
      text: 'text-base',
      badge: 'w-3 h-3',
    },
    md: {
      container: 'w-12 h-12',
      icon: 'w-6 h-6',
      text: 'text-xl',
      badge: 'w-3.5 h-3.5',
    },
    lg: {
      container: 'w-16 h-16',
      icon: 'w-8 h-8',
      text: 'text-2xl',
      badge: 'w-4 h-4',
    },
    xl: {
      container: 'w-20 h-20',
      icon: 'w-10 h-10',
      text: 'text-3xl',
      badge: 'w-5 h-5',
    },
  };

  // Configurações de estilo por tipo de usuário
  const styles = {
    superuser: {
      bg: 'bg-gradient-to-br from-red-500 to-red-700 dark:from-red-600 dark:to-red-800',
      border: 'border-red-400/40 dark:border-red-500/40',
      icon: Shield,
      iconColor: 'text-white',
      shadow: 'shadow-lg shadow-red-500/30 dark:shadow-red-600/20',
      badge: 'bg-red-500',
    },
    staff: {
      bg: 'bg-gradient-to-br from-purple-500 to-purple-700 dark:from-purple-600 dark:to-purple-800',
      border: 'border-purple-400/40 dark:border-purple-500/40',
      icon: Shield,
      iconColor: 'text-white',
      shadow: 'shadow-lg shadow-purple-500/30 dark:shadow-purple-600/20',
      badge: 'bg-purple-500',
    },
    premium: {
      bg: 'bg-gradient-to-br from-yellow-400 to-yellow-600 dark:from-yellow-500 dark:to-yellow-700',
      border: 'border-yellow-300/40 dark:border-yellow-400/40',
      icon: Crown,
      iconColor: 'text-yellow-900 dark:text-white',
      shadow: 'shadow-lg shadow-yellow-500/30 dark:shadow-yellow-600/20',
      badge: 'bg-yellow-500',
    },
    free: {
      bg: 'bg-gradient-to-br from-primary-600 to-primary-700 dark:from-primary-500 dark:to-primary-600',
      border: 'border-primary-400/40 dark:border-primary-500/40',
      icon: User,
      iconColor: 'text-white',
      shadow: 'shadow-lg shadow-primary-500/30 dark:shadow-primary-600/20',
      badge: 'bg-primary-500',
    },
  };

  const currentSize = sizes[size];
  const currentStyle = styles[userType];
  const IconComponent = currentStyle.icon;

  return (
    <div className="relative inline-block">
      <div
        className={`
          ${currentSize.container}
          ${currentStyle.bg}
          ${currentStyle.shadow}
          rounded-full sm:rounded-2xl
          flex items-center justify-center
          border ${currentStyle.border}
          transition-all duration-300
          hover:scale-105
        `}
      >
        <IconComponent
          className={`${currentSize.icon} ${currentStyle.iconColor}`}
          strokeWidth={2.5}
        />
      </div>

      {/* Badge de tipo de usuário */}
      {showBadge && userType !== 'free' && (
        <div
          className={`
            absolute -bottom-1 -right-1
            ${currentSize.badge}
            ${currentStyle.badge}
            rounded-full
            border-2 border-white dark:border-gray-900
            flex items-center justify-center
          `}
        >
          {userType === 'premium' && (
            <Star className="w-full h-full p-0.5 text-white fill-white" />
          )}
          {(userType === 'superuser' || userType === 'staff') && (
            <Shield className="w-full h-full p-0.5 text-white fill-white" />
          )}
        </div>
      )}
    </div>
  );
}
