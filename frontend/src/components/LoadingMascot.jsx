import React from 'react';

export default function LoadingMascot({ message = 'Analisando...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="relative mb-6">
        {/* Mascote pensando */}
        <svg 
          width="100" 
          height="100" 
          viewBox="0 0 100 100" 
          fill="none" 
          xmlns="http://www.w3.org/2000/svg"
          className="animate-pulse"
        >
          {/* Cabeça do robô */}
          <rect x="20" y="25" width="60" height="50" rx="12" fill="url(#gradientThinking)" />
          
          {/* Antena com bola de futebol */}
          <line x1="50" y1="25" x2="50" y2="12" stroke="#3b82f6" strokeWidth="3" strokeLinecap="round" />
          <circle cx="50" cy="8" r="5" fill="#3b82f6">
            <animate attributeName="cy" values="8;4;8" dur="1.5s" repeatCount="indefinite" />
          </circle>
          
          {/* Olhos pensando */}
          <circle cx="35" cy="45" r="6" fill="#3b82f6" />
          <circle cx="65" cy="45" r="6" fill="#3b82f6" />
          <circle cx="33" cy="43" r="2" fill="white">
            <animate attributeName="opacity" values="1;0;1" dur="2s" repeatCount="indefinite" />
          </circle>
          <circle cx="63" cy="43" r="2" fill="white">
            <animate attributeName="opacity" values="1;0;1" dur="2s" repeatCount="indefinite" />
          </circle>
          
          {/* Boca/Display animado */}
          <rect x="30" y="58" width="40" height="10" rx="5" fill="#1e293b" opacity="0.3" />
          <line x1="35" y1="63" x2="45" y2="63" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round">
            <animate attributeName="x2" values="45;55;45" dur="1.5s" repeatCount="indefinite" />
          </line>
          <line x1="55" y1="63" x2="65" y2="63" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round">
            <animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite" />
          </line>
          
          {/* Detalhes laterais pulsando */}
          <circle cx="18" cy="50" r="4" fill="#3b82f6" opacity="0.6">
            <animate attributeName="r" values="4;5;4" dur="1s" repeatCount="indefinite" />
          </circle>
          <circle cx="82" cy="50" r="4" fill="#3b82f6" opacity="0.6">
            <animate attributeName="r" values="4;5;4" dur="1s" repeatCount="indefinite" />
          </circle>
          
          {/* Gradientes */}
          <defs>
            <linearGradient id="gradientThinking" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#3b82f6" />
              <stop offset="100%" stopColor="#2563eb" />
            </linearGradient>
          </defs>
        </svg>

        {/* Bolhas de pensamento */}
        <div className="absolute -top-2 -right-2">
          <div className="relative">
            <div className="w-3 h-3 bg-blue-400 rounded-full animate-bounce"></div>
            <div className="absolute top-2 left-2 w-2 h-2 bg-blue-300 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="absolute top-4 left-4 w-4 h-4 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
        </div>

        {/* Efeito de ondas */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-28 h-28 bg-blue-100 rounded-full opacity-30 animate-ping"></div>
        </div>
      </div>

      <p className="text-lg font-semibold text-blue-600 mb-1 animate-pulse">
        {message}
      </p>
      <p className="text-sm text-gray-500">
        Nossa IA está trabalhando para você
      </p>

      {/* Loading dots */}
      <div className="flex gap-1 mt-4">
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
      </div>
    </div>
  );
}
