from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.throttling import ScopedRateThrottle
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from apps.subscriptions.plan_config import get_plan_limit
from .models import User
from .serializers import UserRegistrationSerializer, UserSerializer, UserProfileUpdateSerializer
from .tokens import account_activation_token, password_reset_token, decode_uid


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
        
        # Atribuir indicação de afiliado (código do corpo ou cookie).
        self._assign_affiliate(request, user)

        # Notificações por email (boas-vindas + verificação).
        self._send_welcome_emails(user)
        
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

    def _assign_affiliate(self, request, user):
        """Vincula o utilizador ao afiliado (link ou código promocional)."""
        try:
            from apps.affiliates.services import assign_referral

            code = request.data.get('ref') or request.data.get('promo_code') or ''
            source = 'promo_code' if request.data.get('promo_code') else 'link'
            if not code:
                code = request.COOKIES.get('affiliate_ref', '')
                source = 'link'
            if code:
                assign_referral(user, code, source=source)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning('Falha ao atribuir afiliado: %s', exc)

    def _send_welcome_emails(self, user):
        """Envia email de boas-vindas e de verificação (não bloqueia o registo)."""
        try:
            from .emails import send_welcome_email, send_verification_email
            send_welcome_email(user)
            if not user.email_verified:
                send_verification_email(user)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning('Falha ao enviar emails de boas-vindas: %s', exc)


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


def _get_user_from_uidb64(uidb64):
    """Recupera o utilizador a partir do uidb64 (ou None)."""
    pk = decode_uid(uidb64)
    if not pk:
        return None
    try:
        return User.objects.get(pk=pk)
    except (User.DoesNotExist, ValueError, TypeError):
        return None


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """Confirma o email de um utilizador via link (uid + token)."""
    uidb64 = request.data.get('uid')
    token = request.data.get('token')
    user = _get_user_from_uidb64(uidb64)

    if user and account_activation_token.check_token(user, token):
        if not user.email_verified:
            user.email_verified = True
            user.save(update_fields=['email_verified'])
        return Response({'message': 'Email verificado com sucesso.'})
    return Response(
        {'error': 'Link de verificação inválido ou expirado.'},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification(request):
    """Reenvia o email de verificação (não revela se o email existe)."""
    email = (request.data.get('email') or '').strip().lower()
    user = User.objects.filter(email__iexact=email).first()
    if user and not user.email_verified:
        from .emails import send_verification_email
        send_verification_email(user)
    return Response({
        'message': 'Se o email estiver registado, enviámos um novo link de verificação.',
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Envia email com link de redefinição de senha (não revela cadastro)."""
    email = (request.data.get('email') or '').strip().lower()
    user = User.objects.filter(email__iexact=email).first()
    if user:
        from .emails import send_password_reset_email
        send_password_reset_email(user)
    return Response({
        'message': 'Se o email estiver registado, enviámos as instruções de recuperação.',
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Redefine a senha a partir do link (uid + token + nova senha)."""
    uidb64 = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('new_password')

    user = _get_user_from_uidb64(uidb64)
    if not user or not password_reset_token.check_token(user, token):
        return Response(
            {'error': 'Link de redefinição inválido ou expirado.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_password(new_password, user)
    except Exception as exc:
        return Response({'error': list(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    from .emails import send_password_changed_email
    send_password_changed_email(user)

    return Response({'message': 'Senha redefinida com sucesso.'})
