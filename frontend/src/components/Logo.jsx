import React from 'react';

export default function Logo({ variant = 'default', size = 'md', showText = true }) {
  const sizes = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24',
  };

  const textSizes = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-2xl',
    xl: 'text-3xl',
  };

  // Variações da mascote
  const variants = {
    default: {
      eyeColor: '#16a34a',
      expression: 'normal',
    },
    thinking: {
      eyeColor: '#3b82f6',
      expression: 'thinking',
    },
    happy: {
      eyeColor: '#16a34a',
      expression: 'happy',
    },
    premium: {
      eyeColor: '#eab308',
      expression: 'happy',
    },
  };

  const currentVariant = variants[variant] || variants.default;

  return (
    <div className="flex items-center gap-3">
      <div className={`${sizes[size]} relative`}>
        <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
          {/* Cabeça do robô */}
          <rect x="20" y="25" width="60" height="50" rx="12" fill="url(#gradient1)" />
          
          {/* Antena com bola de futebol */}
          <line x1="50" y1="25" x2="50" y2="12" stroke="#16a34a" strokeWidth="3" strokeLinecap="round" />
          <circle cx="50" cy="8" r="5" fill="#16a34a" />
          <circle cx="50" cy="8" r="3" fill="white" opacity="0.3" />
          
          {/* Olhos */}
          {currentVariant.expression === 'thinking' ? (
            <>
              <circle cx="35" cy="45" r="6" fill={currentVariant.eyeColor} />
              <circle cx="65" cy="45" r="6" fill={currentVariant.eyeColor} />
              <circle cx="33" cy="43" r="2" fill="white" />
              <circle cx="63" cy="43" r="2" fill="white" />
            </>
          ) : currentVariant.expression === 'happy' ? (
            <>
              <path d="M29 45 Q35 40 41 45" stroke={currentVariant.eyeColor} strokeWidth="3" strokeLinecap="round" fill="none" />
              <path d="M59 45 Q65 40 71 45" stroke={currentVariant.eyeColor} strokeWidth="3" strokeLinecap="round" fill="none" />
            </>
          ) : (
            <>
              <circle cx="35" cy="45" r="6" fill={currentVariant.eyeColor} />
              <circle cx="65" cy="45" r="6" fill={currentVariant.eyeColor} />
              <circle cx="33" cy="43" r="2.5" fill="white" />
              <circle cx="63" cy="43" r="2.5" fill="white" />
            </>
          )}
          
          {/* Boca/Display */}
          <rect x="30" y="58" width="40" height="10" rx="5" fill="#1e293b" opacity="0.3" />
          <line x1="35" y1="63" x2="45" y2="63" stroke={currentVariant.eyeColor} strokeWidth="2" strokeLinecap="round" />
          <line x1="55" y1="63" x2="65" y2="63" stroke={currentVariant.eyeColor} strokeWidth="2" strokeLinecap="round" />
          
          {/* Detalhes laterais */}
          <circle cx="18" cy="50" r="4" fill="#16a34a" opacity="0.6" />
          <circle cx="82" cy="50" r="4" fill="#16a34a" opacity="0.6" />
          
          {/* Badge Premium (se variante premium) */}
          {variant === 'premium' && (
            <>
              <circle cx="75" cy="30" r="8" fill="#eab308" />
              <path d="M75 26 L77 32 L72 32 Z" fill="white" />
            </>
          )}
          
          {/* Gradientes */}
          <defs>
            <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#16a34a" />
              <stop offset="100%" stopColor="#15803d" />
            </linearGradient>
          </defs>
        </svg>
      </div>
      
      {showText && (
        <div className="flex flex-col">
          <span className={`${textSizes[size]} font-bold text-gray-900 leading-tight`}>
            BetInsight
          </span>
          <span className="text-xs text-primary-600 font-medium">
            Powered by AI
          </span>
        </div>
      )}
    </div>
  );
}
