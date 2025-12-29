from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
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
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2', 'phone']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone', '')
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer para exibir dados do usuário"""
    success_rate = serializers.SerializerMethodField()
    can_analyze_today = serializers.SerializerMethodField()
    remaining_analyses = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'phone', 'is_premium', 'premium_until',
            'daily_analysis_count', 'total_analyses', 'successful_predictions',
            'success_rate', 'can_analyze_today', 'remaining_analyses', 'push_enabled'
        ]
        read_only_fields = [
            'id', 'is_premium', 'premium_until', 'daily_analysis_count',
            'total_analyses', 'successful_predictions'
        ]
    
    def get_success_rate(self, obj):
        return obj.get_success_rate()
    
    def get_can_analyze_today(self, obj):
        return obj.can_analyze()
    
    def get_remaining_analyses(self, obj):
        from django.conf import settings
        today = timezone.now().date()
        
        if obj.last_analysis_date != today:
            count = 0
        else:
            count = obj.daily_analysis_count
        
        if obj.is_premium_active():
            return settings.PREMIUM_ANALYSIS_LIMIT - count
        return settings.FREE_ANALYSIS_LIMIT - count


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualizar perfil"""
    class Meta:
        model = User
        fields = ['phone', 'fcm_token', 'push_enabled']
