import React from 'react';

export default function Logo({ variant = 'default', size = 'md', showText = true }) {
  const sizes = {
    sm: 'w-10 h-10',
    md: 'w-14 h-14',
    lg: 'w-20 h-20',
    xl: 'w-28 h-28',
  };

  const textSizes = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-2xl',
    xl: 'text-3xl',
  };

  // Variações de cor baseadas no contexto (harmonizadas com a identidade verde)
  const variants = {
    default: {
      primary: '#16a34a',
      secondary: '#15803d',
      accent: '#22c55e',
      tech: '#10b981',
    },
    thinking: {
      primary: '#16a34a',
      secondary: '#15803d',
      accent: '#4ade80',
      tech: '#22c55e',
    },
    happy: {
      primary: '#16a34a',
      secondary: '#15803d',
      accent: '#4ade80',
      tech: '#22c55e',
    },
    premium: {
      primary: '#eab308',
      secondary: '#ca8a04',
      accent: '#fbbf24',
      tech: '#f59e0b',
    },
  };

  const currentVariant = variants[variant] || variants.default;

  return (
    <div className="flex items-center gap-3">
      <div className={`${sizes[size]} relative`}>
        <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="drop-shadow-lg filter">
          {/* Shield/Escudo Base */}
          <path 
            d="M50 10 L80 20 L80 45 Q80 70 50 90 Q20 70 20 45 L20 20 Z" 
            fill="url(#shieldGradient)"
            opacity="0.95"
            filter="url(#glow)"
          />
          
          {/* Linhas de circuito tecnológico */}
          <g opacity="0.4">
            <path d="M30 30 L35 30 L35 35" stroke={currentVariant.tech} strokeWidth="1.5" />
            <path d="M70 30 L65 30 L65 35" stroke={currentVariant.tech} strokeWidth="1.5" />
            <path d="M30 60 L35 60 L35 55" stroke={currentVariant.tech} strokeWidth="1.5" />
            <path d="M70 60 L65 60 L65 55" stroke={currentVariant.tech} strokeWidth="1.5" />
            <circle cx="35" cy="35" r="1.5" fill={currentVariant.tech} />
            <circle cx="65" cy="35" r="1.5" fill={currentVariant.tech} />
            <circle cx="35" cy="55" r="1.5" fill={currentVariant.tech} />
            <circle cx="65" cy="55" r="1.5" fill={currentVariant.tech} />
          </g>
          
          {/* Bola de futebol híbrida (metade real, metade digital) */}
          <g transform="translate(50, 45)">
            {/* Lado esquerdo - futebol tradicional */}
            <clipPath id="leftHalf">
              <rect x="-15" y="-15" width="15" height="30" />
            </clipPath>
            <circle cx="0" cy="0" r="15" fill="white" clipPath="url(#leftHalf)" />
            <path d="M0,-8 L-3,-3 L-1,3 L1,3 L3,-3 Z" fill={currentVariant.primary} clipPath="url(#leftHalf)" />
            
            {/* Lado direito - digital/pixelado */}
            <clipPath id="rightHalf">
              <rect x="0" y="-15" width="15" height="30" />
            </clipPath>
            <circle cx="0" cy="0" r="15" fill="url(#techGradient)" clipPath="url(#rightHalf)" />
            {/* Pixels tecnológicos */}
            <rect x="2" y="-6" width="3" height="3" fill="white" opacity="0.8" />
            <rect x="6" y="-3" width="3" height="3" fill="white" opacity="0.6" />
            <rect x="2" y="0" width="3" height="3" fill="white" opacity="0.7" />
            <rect x="6" y="3" width="3" height="3" fill="white" opacity="0.5" />
            <rect x="10" y="0" width="3" height="3" fill="white" opacity="0.4" />
            
            {/* Linha divisória tech */}
            <line x1="0" y1="-15" x2="0" y2="15" stroke={currentVariant.accent} strokeWidth="1.5" strokeDasharray="2,2" opacity="0.6" />
            
            {/* Brilho */}
            <circle cx="-6" cy="-6" r="3" fill="white" opacity="0.4" />
          </g>
          
          {/* Check mark integrado (símbolo de "certo") */}
          <g transform="translate(50, 68)">
            <circle cx="0" cy="0" r="8" fill="white" opacity="0.95" />
            <circle cx="0" cy="0" r="7" fill={currentVariant.primary} />
            <path 
              d="M-3,0 L-1,3 L4,-3" 
              stroke="white" 
              strokeWidth="2" 
              strokeLinecap="round"
              strokeLinejoin="round"
              fill="none" 
            />
          </g>
          
          {/* Partículas/ondas de dados ao redor */}
          <g opacity="0.3">
            <circle cx="25" cy="40" r="1.5" fill={currentVariant.tech} />
            <circle cx="75" cy="40" r="1.5" fill={currentVariant.tech} />
            <circle cx="30" cy="50" r="1" fill={currentVariant.accent} />
            <circle cx="70" cy="50" r="1" fill={currentVariant.accent} />
          </g>
          
          {/* Badge Premium (se variante premium) */}
          {variant === 'premium' && (
            <g transform="translate(75, 25)">
              <circle cx="0" cy="0" r="10" fill={currentVariant.primary} />
              <circle cx="0" cy="0" r="8" fill="url(#starGradient)" />
              <path 
                d="M0,-5 L1.5,-1.5 L5,-1 L2,2 L2.5,5.5 L0,3.5 L-2.5,5.5 L-2,2 L-5,-1 L-1.5,-1.5 Z" 
                fill="white" 
              />
            </g>
          )}
          
          {/* Gradientes */}
          <defs>
            {/* Filtro de brilho/glow para destaque */}
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur in="SourceAlpha" stdDeviation="2" result="blur" />
              <feFlood floodColor="white" floodOpacity="0.5" result="color" />
              <feComposite in="color" in2="blur" operator="in" result="glow" />
              <feMerge>
                <feMergeNode in="glow" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            
            <linearGradient id="shieldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={currentVariant.primary} />
              <stop offset="50%" stopColor={currentVariant.secondary} />
              <stop offset="100%" stopColor={currentVariant.primary} />
            </linearGradient>
            
            <linearGradient id="techGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={currentVariant.tech} />
              <stop offset="100%" stopColor={currentVariant.secondary} />
            </linearGradient>
            
            <radialGradient id="starGradient">
              <stop offset="0%" stopColor={currentVariant.accent} />
              <stop offset="100%" stopColor={currentVariant.primary} />
            </radialGradient>
          </defs>
        </svg>
      </div>
      
      {showText && (
        <div className="flex flex-col">
          <span className={`${textSizes[size]} font-bold bg-gradient-to-r from-green-600 to-green-700 dark:from-green-400 dark:to-green-500 bg-clip-text text-transparent leading-tight`}>
            PlacarCerto
          </span>
          <span className="text-xs text-green-600 dark:text-green-400 font-medium tracking-wide">
            Futebol + IA
          </span>
        </div>
      )}
    </div>
  );
}
