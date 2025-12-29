from rest_framework import serializers
from .models import Analysis
from apps.matches.serializers import MatchDetailSerializer


class AnalysisSerializer(serializers.ModelSerializer):
    """Serializer para análise"""
    match = MatchDetailSerializer(read_only=True)
    confidence_display = serializers.SerializerMethodField()
    prediction_display = serializers.CharField(source='get_prediction_display', read_only=True)
    
    class Meta:
        model = Analysis
        fields = [
            'id', 'match', 'prediction', 'prediction_display', 'confidence',
            'confidence_display', 'home_probability', 'draw_probability',
            'away_probability', 'home_xg', 'away_xg', 'reasoning',
            'key_factors', 'analysis_data', 'is_correct', 'actual_result',
            'created_at'
        ]
        read_only_fields = ['id', 'is_correct', 'actual_result', 'created_at']
    
    def get_confidence_display(self, obj):
        return obj.get_confidence_stars()


class AnalysisRequestSerializer(serializers.Serializer):
    """Serializer para solicitar análise"""
    match_id = serializers.IntegerField(required=True)
    
    def validate_match_id(self, value):
        from apps.matches.models import Match
        try:
            match = Match.objects.get(id=value)
            if not match.is_upcoming():
                raise serializers.ValidationError("Apenas partidas futuras podem ser analisadas.")
            if not match.is_analysis_available:
                raise serializers.ValidationError("Análise não disponível para esta partida.")
        except Match.DoesNotExist:
            raise serializers.ValidationError("Partida não encontrada.")
        return value
