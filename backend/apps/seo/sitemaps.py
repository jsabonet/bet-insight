"""Sitemap das páginas públicas do frontend."""
from django.contrib.sitemaps import Sitemap


class StaticViewSitemap(Sitemap):
    """Inclui apenas páginas públicas que existem no router do frontend."""
    priority = 0.8
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return ['home', 'about', 'faq', 'terms', 'privacy', 'affiliate_terms']

    def location(self, item):
        routes = {
            'home': '/',
            'about': '/about',
            'faq': '/faq',
            'terms': '/terms',
            'privacy': '/privacy',
            'affiliate_terms': '/affiliate/terms',
        }
        return routes[item]


# Dicionário de sitemaps
sitemaps = {'static': StaticViewSitemap}
