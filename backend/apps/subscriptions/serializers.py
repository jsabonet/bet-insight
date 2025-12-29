from rest_framework import serializers
from .models import Subscription, Payment
import re


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer para assinatura"""
    plan_display = serializers.CharField(source='get_plan_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'plan', 'plan_display', 'status', 'status_display',
            'start_date', 'end_date', 'auto_renew', 'amount_paid',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'start_date', 'end_date', 'created_at']
    
    def get_is_active(self, obj):
        return obj.is_active()


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer para pagamento"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'phone_number', 'transaction_id',
            'mpesa_reference', 'status', 'status_display',
            'created_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'transaction_id', 'mpesa_reference', 'status',
            'created_at', 'completed_at'
        ]


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer para criar pagamento"""
    plan = serializers.ChoiceField(choices=['monthly', 'quarterly', 'yearly'])
    phone_number = serializers.CharField(max_length=15)
    
    def validate_phone_number(self, value):
        # Validar formato Moçambique: +258 ou 258 ou 84/85/86/87
        pattern = r'^(\+?258)?[8][2-7][0-9]{7}$'
        clean_phone = value.replace(' ', '').replace('-', '')
        if not re.match(pattern, clean_phone):
            raise serializers.ValidationError(
                "Número de telefone inválido. Use formato: +258 8X XXX XXXX"
            )
        return clean_phone
