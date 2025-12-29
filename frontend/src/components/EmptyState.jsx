import React from 'react';

export default function EmptyState({ 
  variant = 'default', 
  title, 
  description, 
  action 
}) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 animate-slide-up">
      <div className="relative mb-6">
        {/* Mascote com expressão baseada no estado */}
        <svg 
          width="120" 
          height="120" 
          viewBox="0 0 100 100" 
          fill="none" 
          xmlns="http://www.w3.org/2000/svg"
          className="animate-pulse-soft"
        >
          {/* Cabeça do robô */}
          <rect x="20" y="25" width="60" height="50" rx="12" fill="url(#gradientEmpty)" />
          
          {/* Antena */}
          <line x1="50" y1="25" x2="50" y2="12" stroke="#94a3b8" strokeWidth="3" strokeLinecap="round" />
          <circle cx="50" cy="8" r="5" fill="#94a3b8" />
          
          {/* Olhos tristes/vazios */}
          {variant === 'no-matches' ? (
            <>
              <circle cx="35" cy="45" r="6" fill="#94a3b8" />
              <circle cx="65" cy="45" r="6" fill="#94a3b8" />
              <circle cx="33" cy="47" r="2" fill="white" />
              <circle cx="63" cy="47" r="2" fill="white" />
            </>
          ) : variant === 'no-analyses' ? (
            <>
              <path d="M29 48 Q35 53 41 48" stroke="#94a3b8" strokeWidth="3" strokeLinecap="round" fill="none" />
              <path d="M59 48 Q65 53 71 48" stroke="#94a3b8" strokeWidth="3" strokeLinecap="round" fill="none" />
            </>
          ) : (
            <>
              <circle cx="35" cy="45" r="6" fill="#94a3b8" />
              <circle cx="65" cy="45" r="6" fill="#94a3b8" />
            </>
          )}
          
          {/* Boca triste */}
          <path d="M35 62 Q50 58 65 62" stroke="#94a3b8" strokeWidth="3" strokeLinecap="round" fill="none" />
          
          {/* Detalhes laterais */}
          <circle cx="18" cy="50" r="4" fill="#cbd5e1" />
          <circle cx="82" cy="50" r="4" fill="#cbd5e1" />
          
          {/* Ícone contextual */}
          {variant === 'no-matches' && (
            <g transform="translate(35, 80)">
              <circle cx="15" cy="15" r="12" fill="#f1f5f9" />
              <path d="M15 10 v10 M10 15 h10" stroke="#94a3b8" strokeWidth="2" strokeLinecap="round" />
            </g>
          )}
          
          {variant === 'no-analyses' && (
            <g transform="translate(35, 80)">
              <circle cx="15" cy="15" r="12" fill="#f1f5f9" />
              <path d="M10 15 L15 20 L20 12" stroke="#94a3b8" strokeWidth="2" strokeLinecap="round" fill="none" />
            </g>
          )}
          
          <defs>
            <linearGradient id="gradientEmpty" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#e2e8f0" />
              <stop offset="100%" stopColor="#cbd5e1" />
            </linearGradient>
          </defs>
        </svg>

        {/* Efeito de ondas ao redor */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-primary-100 rounded-full opacity-20 animate-ping"></div>
        </div>
      </div>

      <h3 className="text-xl font-bold text-gray-900 mb-2 text-center">
        {title}
      </h3>
      
      <p className="text-gray-600 text-center mb-6 max-w-sm">
        {description}
      </p>

      {action && (
        <div className="mt-2">
          {action}
        </div>
      )}
    </div>
  );
}
