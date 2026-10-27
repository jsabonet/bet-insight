import { Helmet } from 'react-helmet-async';
import PropTypes from 'prop-types';

/**
 * Componente SEO Head - Otimização completa para motores de busca
 * Inclui: Meta tags, Open Graph, Twitter Cards, JSON-LD, Canonical URLs
 */
const SEOHead = ({
  title = 'PlacerCerto - Análise Estatística de Futebol',
  description = 'Análises estatísticas e probabilidades estimadas de futebol com dados de partidas em Moçambique, África e Europa. Informação educativa, não um serviço de apostas.',
  keywords = 'previsões futebol, análise estatística futebol, modelos matemáticos futebol, probabilidades futebol, estatísticas futebol, Moçambique futebol, PlacerCerto, análise quantitativa, poisson futebol, regressão logística',
  ogImage = 'https://placarcerto.digital/og-image.png',
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
  const currentUrl = canonicalUrl || new URL(window.location.pathname, siteUrl).href;
  const fullTitle = title.includes('PlacerCerto') ? title : `${title} | PlacerCerto`;

  // Structured Data padrão (Organization)
  const defaultStructuredData = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'PlacerCerto',
    url: siteUrl,
    logo: `${siteUrl}/logo-email.png`,
    description: 'Plataforma de análise estatística de futebol com modelos matemáticos',
    contactPoint: {
      '@type': 'ContactPoint',
      contactType: 'Customer Service',
      availableLanguage: ['Portuguese', 'English']
    }
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
      <meta property="og:locale" content="pt_MZ" />
      
      {publishedTime && <meta property="article:published_time" content={publishedTime} />}
      {modifiedTime && <meta property="article:modified_time" content={modifiedTime} />}
      
      {/* Twitter */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:url" content={currentUrl} />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={ogImage} />
      <meta name="twitter:creator" content="@placarcerto" />
      
      {/* Mobile Optimization */}
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0" />
      <meta name="mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
      
      {/* Language and Region */}
      <meta httpEquiv="content-language" content="pt-MZ" />
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
