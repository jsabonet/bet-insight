"""
Sistema de Sitemap Dinâmico para SEO
Gera sitemaps XML atualizados automaticamente com todas as páginas importantes
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from apps.matches.models import Match, League, Team
from apps.analysis.models import Analysis


class StaticViewSitemap(Sitemap):
    """Sitemap para páginas estáticas"""
    priority = 1.0
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return ['home', 'leagues', 'matches', 'about', 'pricing', 'faq']

    def location(self, item):
        # Mapeamento de rotas do frontend
        routes = {
            'home': '/',
            'leagues': '/leagues',
            'matches': '/matches',
            'about': '/about',
            'pricing': '/premium',
            'faq': '/faq'
        }
        return routes.get(item, '/')


class MatchSitemap(Sitemap):
    """Sitemap para partidas"""
    changefreq = 'hourly'
    priority = 0.8
    protocol = 'https'
    limit = 5000

    def items(self):
        # Últimas 1000 partidas (90 dias) + próximas 30 dias
        date_90_days_ago = timezone.now() - timedelta(days=90)
        date_30_days_future = timezone.now() + timedelta(days=30)
        
        return Match.objects.filter(
            match_date__gte=date_90_days_ago,
            match_date__lte=date_30_days_future
        ).select_related('home_team', 'away_team', 'league').order_by('-match_date')[:1000]

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f'/matches/{obj.id}'


class LeagueSitemap(Sitemap):
    """Sitemap para ligas"""
    changefreq = 'weekly'
    priority = 0.7
    protocol = 'https'

    def items(self):
        return League.objects.filter(is_active=True).order_by('-priority', 'name')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f'/leagues/{obj.id}'


class TeamSitemap(Sitemap):
    """Sitemap para times"""
    changefreq = 'weekly'
    priority = 0.6
    protocol = 'https'
    limit = 2000

    def items(self):
        # Times que jogaram recentemente ou vão jogar
        date_60_days_ago = timezone.now() - timedelta(days=60)
        date_30_days_future = timezone.now() + timedelta(days=30)
        
        team_ids = Match.objects.filter(
            match_date__gte=date_60_days_ago,
            match_date__lte=date_30_days_future
        ).values_list('home_team_id', 'away_team_id')
        
        # Flatten the list of tuples
        all_team_ids = set()
        for home_id, away_id in team_ids:
            all_team_ids.add(home_id)
            all_team_ids.add(away_id)
        
        return Team.objects.filter(id__in=all_team_ids).order_by('name')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f'/teams/{obj.id}'


class AnalysisSitemap(Sitemap):
    """Sitemap para análises públicas"""
    changefreq = 'daily'
    priority = 0.7
    protocol = 'https'
    limit = 1000

    def items(self):
        # Últimas 500 análises (últimos 30 dias)
        date_30_days_ago = timezone.now() - timedelta(days=30)
        
        return Analysis.objects.filter(
            created_at__gte=date_30_days_ago
        ).select_related('match', 'user').order_by('-created_at')[:500]

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return f'/analyses/{obj.id}'


# Dicionário de sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'matches': MatchSitemap,
    'leagues': LeagueSitemap,
    'teams': TeamSitemap,
    'analyses': AnalysisSitemap,
}
