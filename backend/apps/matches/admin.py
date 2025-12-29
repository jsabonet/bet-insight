from django.contrib import admin
from .models import League, Team, Match


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'is_active', 'priority', 'created_at']
    list_filter = ['is_active', 'country']
    search_fields = ['name', 'country']
    ordering = ['-priority', 'name']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'created_at']
    search_fields = ['name', 'country']
    ordering = ['name']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['home_team', 'away_team', 'league', 'match_date', 'status', 'home_score', 'away_score']
    list_filter = ['status', 'league', 'match_date']
    search_fields = ['home_team__name', 'away_team__name', 'league__name']
    date_hierarchy = 'match_date'
    ordering = ['-match_date']
    
    fieldsets = (
        ('Informações da Partida', {
            'fields': ('league', 'home_team', 'away_team', 'match_date', 'round')
        }),
        ('Status e Resultado', {
            'fields': ('status', 'home_score', 'away_score', 'is_analysis_available')
        }),
        ('IDs Externos', {
            'fields': ('api_football_id', 'football_data_id')
        }),
        ('Cache', {
            'fields': ('stats_cache', 'last_stats_update'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
