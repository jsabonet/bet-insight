// Helper para gerar fallback de logos quando não disponíveis

// Logo padrão baseado na inicial do time
export const getTeamLogoFallback = (teamName) => {
  const initial = teamName.charAt(0).toUpperCase();
  const colors = [
    'from-red-500 to-red-600',
    'from-blue-500 to-blue-600',
    'from-green-500 to-green-600',
    'from-yellow-500 to-yellow-600',
    'from-purple-500 to-purple-600',
    'from-pink-500 to-pink-600',
    'from-indigo-500 to-indigo-600',
  ];
  
  const colorIndex = teamName.charCodeAt(0) % colors.length;
  return {
    initial,
    gradient: colors[colorIndex]
  };
};

// URLs de logos de ligas populares (fallback)
export const leagueLogos = {
  'Premier League': 'https://media.api-sports.io/football/leagues/39.png',
  'La Liga': 'https://media.api-sports.io/football/leagues/140.png',
  'Bundesliga': 'https://media.api-sports.io/football/leagues/78.png',
  'Serie A': 'https://media.api-sports.io/football/leagues/135.png',
  'Ligue 1': 'https://media.api-sports.io/football/leagues/61.png',
  'Champions League': 'https://media.api-sports.io/football/leagues/2.png',
  'Europa League': 'https://media.api-sports.io/football/leagues/3.png',
  'Premier League Moçambique': 'https://cdn.countryflags.com/thumbs/mozambique/flag-round-250.png',
};

// Verifica se a URL do logo é válida
export const isValidLogoUrl = (url) => {
  if (!url) return false;
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

// Componente de imagem de logo com fallback
export const TeamLogo = ({ team, size = 'md', className = '' }) => {
  const sizes = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16',
  };

  const imgSizes = {
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12',
  };

  const hasValidLogo = isValidLogoUrl(team.logo);
  const fallback = getTeamLogoFallback(team.name);

  if (hasValidLogo) {
    return (
      <div className={`${sizes[size]} bg-white rounded-xl flex items-center justify-center border border-gray-200 shadow-sm ${className}`}>
        <img 
          src={team.logo} 
          alt={team.name}
          className={`${imgSizes[size]} object-contain`}
          onError={(e) => {
            e.target.style.display = 'none';
            e.target.parentElement.innerHTML = `<span class="text-lg font-bold text-gray-600">${fallback.initial}</span>`;
          }}
        />
      </div>
    );
  }

  return (
    <div className={`${sizes[size]} bg-gradient-to-br ${fallback.gradient} rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-sm ${className}`}>
      {fallback.initial}
    </div>
  );
};

// Componente de logo de liga
export const LeagueLogo = ({ league, size = 'sm', className = '' }) => {
  const sizes = {
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  const logoUrl = league.logo || leagueLogos[league.name];

  if (logoUrl && isValidLogoUrl(logoUrl)) {
    return (
      <img 
        src={logoUrl} 
        alt={league.name}
        className={`${sizes[size]} object-contain ${className}`}
        onError={(e) => {
          e.target.style.display = 'none';
        }}
      />
    );
  }

  return (
    <div className={`${sizes[size]} bg-primary-100 rounded-full flex items-center justify-center ${className}`}>
      <span className="text-primary-600 text-xs font-bold">
        {league.country?.slice(0, 2).toUpperCase() || '⚽'}
      </span>
    </div>
  );
};
