"""Serializers do sistema de afiliados."""
from decimal import Decimal

from rest_framework import serializers
from django.db.models import Count, Sum
from django.utils import timezone

from .models import Affiliate, AffiliateReferral, AffiliateCommission


class AffiliateSerializer(serializers.ModelSerializer):
    """Dados públicos do afiliado para o seu próprio painel."""
    referral_link = serializers.SerializerMethodField()
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)

    class Meta:
        model = Affiliate
        fields = [
            'id', 'code', 'status', 'tier', 'tier_display',
            'commission_rate', 'renewal_rate',
            'total_earned', 'available_balance', 'pending_balance',
            'payout_method', 'payout_account', 'referral_link', 'created_at',
        ]
        read_only_fields = [
            'id', 'code', 'status', 'tier', 'commission_rate', 'renewal_rate',
            'total_earned', 'available_balance', 'pending_balance', 'created_at',
        ]

    def get_referral_link(self, obj):
        site = getattr(self.context.get('request'), 'build_absolute_uri', None)
        try:
            base = site('/') if site else ''
        except Exception:
            base = ''
        base = base.rstrip('/')
        return f"{base}/?ref={obj.code}"


class AffiliateApplySerializer(serializers.ModelSerializer):
    """Formulário de candidatura a afiliado."""
    class Meta:
        model = Affiliate
        fields = ['payout_method', 'payout_account']
        extra_kwargs = {
            'payout_account': {'required': False, 'allow_blank': True},
        }


class AffiliateReferralSerializer(serializers.ModelSerializer):
    """Indicação (conta criada via link/código) para o painel do afiliado."""
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    converted = serializers.SerializerMethodField()

    class Meta:
        model = AffiliateReferral
        fields = [
            'id', 'user_name', 'user_email', 'code', 'source', 'source_display',
            'first_touch_at', 'last_touch_at', 'converted_at', 'converted',
        ]

    def get_converted(self, obj):
        return obj.converted_at is not None


class AffiliateCommissionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    plan = serializers.SerializerMethodField()
    buyer_email = serializers.SerializerMethodField()

    class Meta:
        model = AffiliateCommission
        fields = [
            'id', 'amount', 'rate', 'commission_type', 'status', 'status_display',
            'plan', 'buyer_email', 'available_at', 'paid_at', 'created_at',
        ]

    def get_plan(self, obj):
        return (obj.payment.metadata or {}).get('plan_name') or (obj.payment.metadata or {}).get('plan')

    def get_buyer_email(self, obj):
        return obj.payment.user.email if obj.payment and obj.payment.user else None


class AffiliateStatsSerializer(serializers.Serializer):
    """Estatísticas agregadas do afiliado."""
    clicks_total = serializers.IntegerField()
    clicks_30d = serializers.IntegerField()
    conversions_total = serializers.IntegerField()
    conversions_30d = serializers.IntegerField()
    revenue_30d = serializers.DecimalField(max_digits=12, decimal_places=2)
    commissions_pending = serializers.IntegerField()
    commissions_available = serializers.IntegerField()


class WithdrawRequestSerializer(serializers.Serializer):
    """Pedido de levantamento."""
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
