from rest_framework import serializers
from .models import Analysis, DailyBet, SocialProofTicket
from apps.matches.serializers import MatchDetailSerializer


class AnalysisSerializer(serializers.ModelSerializer):
    """Serializer para análise"""
    match = MatchDetailSerializer(read_only=True)
    confidence_display = serializers.SerializerMethodField()
    prediction_display = serializers.CharField(source='get_prediction_display', read_only=True)
    analysis_data = serializers.SerializerMethodField()
    
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
    
    def get_analysis_data(self, obj):
        """Retorna analysis_data com confidence garantido"""
        data = obj.analysis_data or {}
        
        # Garantir que confidence existe
        if 'confidence' not in data or not data['confidence']:
            # Usar confidence do campo direto ou criar fallback
            stars = obj.confidence if obj.confidence else 3
            data['confidence'] = {
                'stars': stars,
                'level': 'Média' if stars == 3 else ('Alta' if stars >= 4 else 'Baixa'),
                'level_pt': 'Média' if stars == 3 else ('Alta' if stars >= 4 else 'Baixa'),
                'score': stars / 5.0
            }
        
        return data


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


class DailyBetSerializer(serializers.ModelSerializer):
    """Serializer para apostas diárias geradas automaticamente"""
    
    bet_type_display = serializers.CharField(source='get_bet_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    roi = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyBet
        fields = [
            'id', 'date', 'bet_type', 'bet_type_display', 'status', 'status_display',
            'selections', 'total_odd', 'fair_odd', 'combined_probability',
            'expected_value', 'suggested_stake', 'actual_result',
            'is_validated', 'created_at', 'validated_at', 'roi'
        ]
        read_only_fields = fields  # Todas são read-only (geradas automaticamente)
    
    def get_roi(self, obj):
        """Retorna ROI da aposta se validada"""
        return obj.get_roi()


class DailyBetListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de apostas diárias"""
    
    bet_type_display = serializers.CharField(source='get_bet_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    selections_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyBet
        fields = [
            'id', 'date', 'bet_type', 'bet_type_display', 'status', 'status_display',
            'selections_count', 'total_odd', 'combined_probability',
            'expected_value', 'suggested_stake', 'is_validated', 'created_at'
        ]
    
    def get_selections_count(self, obj):
        """Retorna quantidade de apostas no bilhete"""
        return len(obj.selections) if obj.selections else 0


class SocialProofTicketSerializer(serializers.ModelSerializer):
    """Snapshot de prova social, apenas para administradores."""

    kind_display = serializers.CharField(source='get_kind_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    legs_count = serializers.IntegerField(read_only=True)
    potential_return_units = serializers.FloatField(read_only=True)
    headline = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()
    approved_by_email = serializers.SerializerMethodField()

    class Meta:
        model = SocialProofTicket
        fields = [
            'id', 'date', 'kind', 'kind_display', 'status', 'status_display',
            'headline', 'ticket_code', 'reserve_code', 'legs', 'legs_count',
            'source_bet_ids', 'total_odd', 'combined_probability', 'stake_units',
            'potential_return_units', 'disclosure', 'watermark_required',
            'snapshot_hash', 'meta', 'created_by', 'created_by_email',
            'approved_by', 'approved_by_email', 'created_at', 'approved_at',
            'last_exported_at', 'export_count',
        ]
        read_only_fields = fields

    def get_headline(self, obj):
        return (obj.meta or {}).get('headline') or obj.get_kind_display()

    def get_created_by_email(self, obj):
        return obj.created_by.email if obj.created_by_id else None

    def get_approved_by_email(self, obj):
        return obj.approved_by.email if obj.approved_by_id else None


class SocialProofTicketListSerializer(serializers.ModelSerializer):
    """Versão resumida para o histórico da página admin."""

    kind_display = serializers.CharField(source='get_kind_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    legs_count = serializers.IntegerField(read_only=True)
    headline = serializers.SerializerMethodField()

    class Meta:
        model = SocialProofTicket
        fields = [
            'id', 'date', 'kind', 'kind_display', 'status', 'status_display',
            'headline', 'ticket_code', 'reserve_code', 'legs_count',
            'total_odd', 'combined_probability', 'watermark_required',
            'export_count', 'created_at', 'approved_at', 'last_exported_at',
        ]

    def get_headline(self, obj):
        return (obj.meta or {}).get('headline') or obj.get_kind_display()

