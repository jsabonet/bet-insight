/**
 * Gera structured data (Schema.org JSON-LD) para diferentes tipos de conteúdo
 */

/**
 * Structured data para partida de futebol
 */
export const generateMatchStructuredData = (match) => {
  const homeTeam = match.home_team || match.homeTeam;
  const awayTeam = match.away_team || match.awayTeam;
  const league = match.league;
  
  return {
    '@context': 'https://schema.org',
    '@type': 'SportsEvent',
    name: `${homeTeam?.name || 'Home'} vs ${awayTeam?.name || 'Away'}`,
    description: `Análise e previsão: ${homeTeam?.name} enfrenta ${awayTeam?.name} em ${league?.name || 'partida'}`,
    startDate: match.match_date || match.matchDate,
    eventStatus: match.status === 'FINISHED' ? 'https://schema.org/EventScheduled' : 'https://schema.org/EventScheduled',
    location: {
      '@type': 'Place',
      name: homeTeam?.name ? `Estádio ${homeTeam.name}` : 'Estádio',
      address: {
        '@type': 'PostalAddress',
        addressCountry: homeTeam?.country || 'MZ'
      }
    },
    homeTeam: {
      '@type': 'SportsTeam',
      name: homeTeam?.name || 'Home Team',
      sport: 'Football'
    },
    awayTeam: {
      '@type': 'SportsTeam',
      name: awayTeam?.name || 'Away Team',
      sport: 'Football'
    },
    ...(match.home_score !== null && match.away_score !== null && {
      score: `${match.home_score}-${match.away_score}`
    }),
    sport: 'Football',
    competitor: [
      {
        '@type': 'SportsTeam',
        name: homeTeam?.name || 'Home',
      },
      {
        '@type': 'SportsTeam',
        name: awayTeam?.name || 'Away',
      }
    ]
  };
};

/**
 * Structured data para lista de partidas
 */
export const generateMatchListStructuredData = (matches) => {
  return {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    itemListElement: matches.map((match, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      item: {
        '@type': 'SportsEvent',
        name: `${match.home_team?.name || 'Home'} vs ${match.away_team?.name || 'Away'}`,
        startDate: match.match_date || match.matchDate,
        url: `https://placarcerto.digital/matches/${match.id}`
      }
    }))
  };
};

/**
 * Structured data para análise
 */
export const generateAnalysisStructuredData = (analysis, match) => {
  return {
    '@context': 'https://schema.org',
    '@type': 'AnalysisNewsArticle',
    headline: `Análise: ${match.home_team?.name} vs ${match.away_team?.name}`,
    description: analysis.reasoning || 'Análise estatística completa da partida',
    author: {
      '@type': 'Organization',
      name: 'PlacerCerto Estatísticas'
    },
    publisher: {
      '@type': 'Organization',
      name: 'PlacerCerto',
      logo: {
        '@type': 'ImageObject',
        url: 'https://placarcerto.digital/logo-512x512.png'
      }
    },
    datePublished: analysis.created_at || new Date().toISOString(),
    dateModified: analysis.updated_at || analysis.created_at || new Date().toISOString(),
    about: {
      '@type': 'SportsEvent',
      name: `${match.home_team?.name} vs ${match.away_team?.name}`
    }
  };
};

/**
 * Structured data para breadcrumbs
 */
export const generateBreadcrumbStructuredData = (items) => {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: item.url
    }))
  };
};

/**
 * Structured data para WebSite com SearchAction
 */
export const generateWebsiteStructuredData = () => {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'PlacerCerto',
    url: 'https://placarcerto.digital',
    description: 'Plataforma de análise estatística avançada de futebol com modelos matemáticos preditivos',
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: 'https://placarcerto.digital/search?q={search_term_string}'
      },
      'query-input': 'required name=search_term_string'
    },
    publisher: {
      '@type': 'Organization',
      name: 'PlacerCerto',
      logo: 'https://placarcerto.digital/logo-512x512.png'
    }
  };
};

/**
 * Structured data para Liga
 */
export const generateLeagueStructuredData = (league) => {
  return {
    '@context': 'https://schema.org',
    '@type': 'SportsOrganization',
    name: league.name,
    sport: 'Football',
    description: `${league.name} - Análises e previsões de partidas`,
    address: {
      '@type': 'PostalAddress',
      addressCountry: league.country
    }
  };
};

/**
 * Structured data para FAQ
 */
export const generateFAQStructuredData = (faqs) => {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map(faq => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: faq.answer
      }
    }))
  };
};

/**
 * Structured data para Review/Rating
 */
export const generateReviewStructuredData = (rating, reviewCount) => {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'PlacerCerto',
    applicationCategory: 'SportsApplication',
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: rating,
      reviewCount: reviewCount,
      bestRating: '5',
      worstRating: '1'
    },
    offers: {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'MZN'
    }
  };
};
