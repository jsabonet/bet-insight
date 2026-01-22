import { Helmet } from 'react-helmet-async';
import PropTypes from 'prop-types';

/**
 * Componente SEO Head - Otimização completa para motores de busca
 * Inclui: Meta tags, Open Graph, Twitter Cards, JSON-LD, Canonical URLs
 */
const SEOHead = ({
  title = 'PlacerCerto - Análise Estatística Avançada de Futebol',
  description = 'Previsões precisas de futebol com modelos estatísticos avançados (Poisson + Regressão). Análise quantitativa de partidas, estatísticas em tempo real e apostas inteligentes. Ligas de Moçambique, África e Europa.',
  keywords = 'previsões futebol, apostas desportivas, análise estatística futebol, modelos matemáticos futebol, estatísticas futebol, Moçambique futebol, apostas inteligentes, PlacerCerto, análise quantitativa, odds futebol, poisson futebol',
  ogImage = 'https://placarcerto.digital/og-image.jpg',
  ogType = 'website',
  canonicalUrl,
  publishedTime,
  modifiedTime,
  author = 'PlacerCerto',
  structuredData,
  noindex = false,
  nofollow = false,
}) => {
  const siteUrl = 'https://placarcerto.digital';
  const currentUrl = canonicalUrl || window.location.href;
  const fullTitle = title.includes('PlacerCerto') ? title : `${title} | PlacerCerto`;

  // Structured Data padrão (Organization)
  const defaultStructuredData = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'PlacerCerto',
    url: siteUrl,
    logo: `${siteUrl}/logo-512x512.png`,
    description: 'Plataforma de análise inteligente de futebol com IA',
    contactPoint: {
      '@type': 'ContactPoint',
      contactType: 'Customer Service',
      availableLanguage: ['Portuguese', 'English']
    },
    sameAs: [
      'https://www.facebook.com/placarcerto',
      'https://twitter.com/placarcerto',
      'https://www.instagram.com/placarcerto'
    ]
  };

  return (
    <Helmet>
      {/* Primary Meta Tags */}
      <title>{fullTitle}</title>
      <meta name="title" content={fullTitle} />
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      <meta name="author" content={author} />
      
      {/* Robots */}
      {(noindex || nofollow) && (
        <meta name="robots" content={`${noindex ? 'noindex' : 'index'},${nofollow ? 'nofollow' : 'follow'}`} />
      )}
      
      {/* Canonical URL */}
      <link rel="canonical" href={currentUrl} />
      
      {/* Open Graph / Facebook */}
      <meta property="og:type" content={ogType} />
      <meta property="og:url" content={currentUrl} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:site_name" content="PlacerCerto" />
      <meta property="og:locale" content="pt_PT" />
      
      {publishedTime && <meta property="article:published_time" content={publishedTime} />}
      {modifiedTime && <meta property="article:modified_time" content={modifiedTime} />}
      
      {/* Twitter */}
      <meta property="twitter:card" content="summary_large_image" />
      <meta property="twitter:url" content={currentUrl} />
      <meta property="twitter:title" content={fullTitle} />
      <meta property="twitter:description" content={description} />
      <meta property="twitter:image" content={ogImage} />
      <meta name="twitter:creator" content="@placarcerto" />
      
      {/* Mobile Optimization */}
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0" />
      <meta name="mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
      
      {/* Language and Region */}
      <meta httpEquiv="content-language" content="pt-PT" />
      <meta name="language" content="Portuguese" />
      <meta name="geo.region" content="MZ" />
      <meta name="geo.placename" content="Moçambique" />
      
      {/* DNS Prefetch for Performance */}
      <link rel="dns-prefetch" href="https://fonts.googleapis.com" />
      <link rel="dns-prefetch" href="https://api.placarcerto.digital" />
      
      {/* Structured Data (JSON-LD) */}
      <script type="application/ld+json">
        {JSON.stringify(structuredData || defaultStructuredData)}
      </script>
    </Helmet>
  );
};

SEOHead.propTypes = {
  title: PropTypes.string,
  description: PropTypes.string,
  keywords: PropTypes.string,
  ogImage: PropTypes.string,
  ogType: PropTypes.string,
  canonicalUrl: PropTypes.string,
  publishedTime: PropTypes.string,
  modifiedTime: PropTypes.string,
  author: PropTypes.string,
  structuredData: PropTypes.object,
  noindex: PropTypes.bool,
  nofollow: PropTypes.bool,
};

export default SEOHead;
