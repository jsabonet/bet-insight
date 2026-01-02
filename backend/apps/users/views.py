from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.throttling import ScopedRateThrottle
from django.utils import timezone
from django.conf import settings
from apps.subscriptions.plan_config import get_plan_limit
from .models import User
from .serializers import UserRegistrationSerializer, UserSerializer, UserProfileUpdateSerializer


class RegisterView(generics.CreateAPIView):
    """View para registro de usuário"""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'register'
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Gerar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Usuário criado com sucesso!'
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """Login com escopo de throttle e rastreio de IP/fingerprint"""
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # Se login OK, registrar IP e fingerprint
        try:
            user = User.objects.get(username=request.data.get('username'))
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = ip.split(',')[0].strip() if ip else request.META.get('REMOTE_ADDR')
            fingerprint = request.data.get('fingerprint')
            user.last_login_ip = ip
            if fingerprint:
                user.last_device_fingerprint = fingerprint[:255]
            user.save(update_fields=['last_login_ip', 'last_device_fingerprint'])
        except Exception:
            pass
        return response


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View para visualizar e atualizar perfil"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserSerializer


class UserStatsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'stats'

    def get(self, request):
        user = request.user
        today = timezone.now().date()

        if user.last_analysis_date != today:
            analyses_today = 0
        else:
            analyses_today = user.daily_analysis_count

        # Determinar assinatura ativa e limite diário a partir dela
        active_sub = user.subscriptions.filter(status='active', end_date__gt=timezone.now()).first()
        if active_sub and active_sub.plan_slug:
            daily_limit = get_plan_limit(active_sub.plan_slug)
        else:
            # Sem assinatura ativa: considerar freemium (ignorar flag premium legado)
            daily_limit = get_plan_limit('freemium')
        remaining = max(daily_limit - analyses_today, 0)

        return Response({
            'total_analyses': user.total_analyses,
            'successful_predictions': user.successful_predictions,
            'success_rate': user.get_success_rate(),
            'daily_analysis_count': user.daily_analysis_count,
            'analyses_count_today': analyses_today,
            'daily_limit': daily_limit,
            'remaining': remaining,
            'can_analyze': user.can_analyze(),
            'is_premium': bool(active_sub),
            'premium_until': active_sub.end_date if active_sub else None,
        })
