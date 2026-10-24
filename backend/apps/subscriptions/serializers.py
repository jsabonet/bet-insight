from rest_framework import serializers
from .models import Subscription, Payment


class PlanSerializer(serializers.Serializer):
    """Serializer para planos (baseado em configuração, não em modelo de BD)
    Ajustado para corresponder aos campos de plan_config.PLANS
    """
    slug = serializers.CharField()
    name = serializers.CharField()
    price = serializers.IntegerField()
    duration_days = serializers.IntegerField(required=False, allow_null=True)
    daily_analysis_limit = serializers.IntegerField()
    features = serializers.ListField(child=serializers.CharField())
    description = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField()
    color = serializers.CharField(required=False, allow_blank=True)
    popular = serializers.BooleanField(required=False, default=False)
    trial_days = serializers.IntegerField(required=False)
    savings = serializers.IntegerField(required=False)
    original_price = serializers.IntegerField(required=False)
    lifetime = serializers.BooleanField(required=False)
    payment_mode = serializers.CharField(required=False)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer para assinatura"""
    plan_display = serializers.CharField(source='get_plan_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active = serializers.SerializerMethodField()
    plan_slug = serializers.SerializerMethodField()
    daily_limit = serializers.SerializerMethodField()
    plan_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'plan', 'plan_slug', 'plan_display', 'status', 'status_display',
            'start_date', 'end_date', 'auto_renew', 'amount_paid',
            'is_active', 'daily_limit', 'plan_details', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'start_date', 'end_date', 'created_at']
    
    def get_is_active(self, obj):
        return obj.is_active()
    
    def get_plan_slug(self, obj):
        """Retorna slug do plano para compatibilidade com frontend"""
        # Se plan_slug existe no banco, usar ele; senão, usar o plan
        if hasattr(obj, 'plan_slug') and obj.plan_slug:
            return obj.plan_slug
        return obj.plan
    
    def get_daily_limit(self, obj):
        """Retorna limite diário baseado no plano"""
        from .plan_config import get_plan
        plan_slug = self.get_plan_slug(obj)
        plan = get_plan(plan_slug)
        return plan.get('daily_analysis_limit', 5) if plan else 5
    
    def get_plan_details(self, obj):
        """Retorna detalhes completos do plano"""
        from .plan_config import get_plan
        plan_slug = self.get_plan_slug(obj)
        plan = get_plan(plan_slug)
        if not plan:
            return None
        return {
            'name': plan.get('name', ''),
            'price': plan.get('price', 0),
            'features': plan.get('features', []),
            'color': plan.get('color', 'blue'),
            'description': plan.get('description', ''),
            'lifetime': plan.get('lifetime', False),
        }


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer para pagamento"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    checkout_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'currency', 'phone_number', 'transaction_id',
            'vpay_order_id', 'gateway',
            'payment_method', 'status', 'status_display', 'checkout_url',
            'metadata', 'created_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'transaction_id', 'vpay_order_id', 'gateway', 'status',
            'created_at', 'completed_at'
        ]
    
    def get_checkout_url(self, obj):
        """URL de checkout hospedado da VPay."""
        metadata = obj.metadata or {}
        return metadata.get('checkout_url') or ''
