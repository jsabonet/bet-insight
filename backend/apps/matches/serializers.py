from rest_framework import serializers
from .models import League, Team, Match


class LeagueSerializer(serializers.ModelSerializer):
    """Serializer para Liga"""
    class Meta:
        model = League
        fields = ['id', 'name', 'country', 'logo', 'is_active', 'priority']


class TeamSerializer(serializers.ModelSerializer):
    """Serializer para Time"""
    class Meta:
        model = Team
        fields = ['id', 'name', 'logo', 'country']


class MatchListSerializer(serializers.ModelSerializer):
    """Serializer para lista de partidas"""
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)
    league = LeagueSerializer(read_only=True)
    
    class Meta:
        model = Match
        fields = [
            'id', 'league', 'home_team', 'away_team', 'match_date',
            'status', 'home_score', 'away_score', 'is_analysis_available'
        ]


class MatchDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para partida"""
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)
    league = LeagueSerializer(read_only=True)
    result = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()
    
    class Meta:
        model = Match
        fields = [
            'id', 'league', 'home_team', 'away_team', 'match_date',
            'status', 'round', 'home_score', 'away_score', 
            'is_analysis_available', 'stats_cache', 'result', 'is_upcoming'
        ]
    
    def get_result(self, obj):
        return obj.get_result()
    
    def get_is_upcoming(self, obj):
        return obj.is_upcoming()
