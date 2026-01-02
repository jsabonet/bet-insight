from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from datetime import date
from dateutil.relativedelta import relativedelta
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuário"""
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )
    age_confirmation = serializers.BooleanField(
        write_only=True,
        required=True,
        error_messages={
            'required': 'Você deve confirmar que tem 18 anos ou mais.'
        }
    )
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2', 'phone', 'age_confirmation']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        
        # Validar confirmação de idade
        if not attrs.get('age_confirmation'):
            raise serializers.ValidationError({
                "age_confirmation": "Você deve confirmar que tem pelo menos 18 anos para se cadastrar."
            })
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        validated_data.pop('age_confirmation')  # Remover pois não é campo do modelo
        request = self.context.get('request')
        # Capturar fingerprint enviada no corpo
        fingerprint = None
        if request:
            fingerprint = request.data.get('fingerprint')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone', '')
        )
        # Guardar IP e fingerprint no cadastro
        if request:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = ip.split(',')[0].strip() if ip else request.META.get('REMOTE_ADDR')
            user.signup_ip = ip
        if fingerprint:
            user.device_fingerprint = fingerprint[:255]
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer para exibir dados do usuário"""
    success_rate = serializers.SerializerMethodField()
    can_analyze_today = serializers.SerializerMethodField()
    remaining_analyses = serializers.SerializerMethodField()
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'phone', 'date_of_birth', 'age',
            'is_premium', 'premium_until',
            'daily_analysis_count', 'total_analyses', 'successful_predictions',
            'success_rate', 'can_analyze_today', 'remaining_analyses', 'push_enabled',
            'is_staff', 'is_superuser'
        ]
        read_only_fields = [
            'id', 'age', 'is_premium', 'premium_until', 'daily_analysis_count',
            'total_analyses', 'successful_predictions', 'is_staff', 'is_superuser'
        ]
    
    def get_success_rate(self, obj):
        return obj.get_success_rate()
    
    def get_can_analyze_today(self, obj):
        return obj.can_analyze()
    
    def get_remaining_analyses(self, obj):
        from apps.subscriptions.plan_config import get_plan_limit
        today = timezone.now().date()
        
        if obj.last_analysis_date != today:
            count = 0
        else:
            count = obj.daily_analysis_count
        
        if obj.is_premium_active():
            from django.conf import settings
            return settings.PREMIUM_ANALYSIS_LIMIT - count
        free_limit = get_plan_limit('freemium')
        return free_limit - count


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualizar perfil"""
    class Meta:
        model = User
        fields = ['phone', 'fcm_token', 'push_enabled']
