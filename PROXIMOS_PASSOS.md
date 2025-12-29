# 📋 PRÓXIMOS PASSOS - BET INSIGHT MOZAMBIQUE

## ✅ Progresso Atual (Concluído)
- ✅ **Fase 1**: Ambiente configurado
- ✅ **Fase 2**: Django Foundation completo
- ✅ **Fase 3**: Todos os modelos implementados e migrados

---

## 🚀 FASE 4: SERIALIZERS (Dia 4 - 6h)

### 4.1. Criar Serializers de Usuário

**Arquivo**: `backend/apps/users/serializers.py`

```python
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
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
```

---

### 4.2. Criar Serializers de Matches

**Arquivo**: `backend/apps/matches/serializers.py`

```python
from rest_framework import serializers
from .models import League, Team, Match


class LeagueSerializer(serializers.ModelSerializer):
    """Serializer para Liga"""
    class Meta:
        model = League
        fields = ['id', 'name', 'country', 'logo', 'is_active']


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
    
    class Meta:
        model = Match
        fields = [
            'id', 'league', 'home_team', 'away_team', 'match_date',
            'status', 'round', 'home_score', 'away_score', 
            'is_analysis_available', 'stats_cache', 'result'
        ]
    
    def get_result(self, obj):
        return obj.get_result()
```

---

### 4.3. Criar Serializers de Analysis

**Arquivo**: `backend/apps/analysis/serializers.py`

```python
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
```

---

### 4.4. Criar Serializers de Subscriptions

**Arquivo**: `backend/apps/subscriptions/serializers.py`

```python
from rest_framework import serializers
from .models import Subscription, Payment


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
        import re
        pattern = r'^(\+?258)?[8][2-7][0-9]{7}$'
        if not re.match(pattern, value.replace(' ', '')):
            raise serializers.ValidationError(
                "Número de telefone inválido. Use formato: +258 8X XXX XXXX"
            )
        return value
```

---

## 🚀 FASE 5: VIEWS E ENDPOINTS (Dia 5-6 - 10h)

### 5.1. Criar Views de Autenticação

**Arquivo**: `backend/apps/users/views.py`

```python
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserRegistrationSerializer, UserSerializer, UserProfileUpdateSerializer


class RegisterView(generics.CreateAPIView):
    """View para registro de usuário"""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
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


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View para visualizar e atualizar perfil"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserProfileUpdateSerializer
        return UserSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request):
    """Estatísticas do usuário"""
    user = request.user
    
    return Response({
        'total_analyses': user.total_analyses,
        'successful_predictions': user.successful_predictions,
        'success_rate': user.get_success_rate(),
        'daily_analysis_count': user.daily_analysis_count,
        'can_analyze': user.can_analyze(),
        'is_premium': user.is_premium_active(),
        'premium_until': user.premium_until,
    })
```

---

### 5.2. Criar Views de Matches

**Arquivo**: `backend/apps/matches/views.py`

```python
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from .models import League, Team, Match
from .serializers import LeagueSerializer, TeamSerializer, MatchListSerializer, MatchDetailSerializer


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Ligas"""
    queryset = League.objects.filter(is_active=True)
    serializer_class = LeagueSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'country']
    ordering_fields = ['priority', 'name']
    ordering = ['-priority']


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Times"""
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'country']


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Partidas"""
    queryset = Match.objects.select_related('league', 'home_team', 'away_team').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['league', 'status']
    ordering_fields = ['match_date']
    ordering = ['match_date']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MatchDetailSerializer
        return MatchListSerializer
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Partidas futuras (próximos 7 dias)"""
        now = timezone.now()
        future = now + timedelta(days=7)
        
        matches = self.get_queryset().filter(
            status='scheduled',
            match_date__gte=now,
            match_date__lte=future,
            is_analysis_available=True
        )
        
        serializer = self.get_serializer(matches, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Partidas de hoje"""
        today = timezone.now().date()
        
        matches = self.get_queryset().filter(
            match_date__date=today,
            is_analysis_available=True
        )
        
        serializer = self.get_serializer(matches, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def live(self, request):
        """Partidas ao vivo"""
        matches = self.get_queryset().filter(status='live')
        serializer = self.get_serializer(matches, many=True)
        return Response(serializer.data)
```

---

### 5.3. Criar Views de Analysis

**Arquivo**: `backend/apps/analysis/views.py`

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Analysis
from .serializers import AnalysisSerializer, AnalysisRequestSerializer
from apps.matches.models import Match


class AnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Análises"""
    serializer_class = AnalysisSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['prediction', 'confidence']
    
    def get_queryset(self):
        """Retorna apenas análises do usuário"""
        return Analysis.objects.filter(user=self.request.user).select_related(
            'match', 'match__league', 'match__home_team', 'match__away_team'
        ).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def request_analysis(self, request):
        """Solicita análise de uma partida"""
        # Validar dados
        serializer = AnalysisRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        match_id = serializer.validated_data['match_id']
        user = request.user
        
        # Verificar se usuário pode analisar
        if not user.can_analyze():
            return Response({
                'error': 'Limite de análises diárias atingido',
                'daily_limit': 5 if not user.is_premium_active() else 100,
                'used': user.daily_analysis_count
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar se já existe análise
        match = Match.objects.get(id=match_id)
        existing = Analysis.objects.filter(user=user, match=match).first()
        
        if existing:
            return Response({
                'message': 'Você já analisou esta partida',
                'analysis': AnalysisSerializer(existing).data
            }, status=status.HTTP_200_OK)
        
        # TODO: Aqui será chamada a função de IA (Fase 6)
        # Por enquanto, retornar dados simulados
        
        from django.conf import settings
        # Simular análise (será substituído por IA real na Fase 6)
        analysis = Analysis.objects.create(
            user=user,
            match=match,
            prediction='home',
            confidence=3,
            home_probability=45.5,
            draw_probability=27.3,
            away_probability=27.2,
            home_xg=1.8,
            away_xg=1.2,
            reasoning="Análise temporária (IA será integrada na Fase 6)",
            key_factors=[
                "Time da casa com melhor forma",
                "Histórico favorável em casa",
                "Visitante com desfalques importantes"
            ],
            analysis_data={
                'form_score': 75,
                'h2h_score': 60,
                'stats_score': 70
            }
        )
        
        # Incrementar contador
        user.increment_analysis_count()
        
        return Response({
            'message': 'Análise gerada com sucesso!',
            'analysis': AnalysisSerializer(analysis).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def my_stats(self, request):
        """Estatísticas das análises do usuário"""
        analyses = self.get_queryset()
        total = analyses.count()
        
        if total == 0:
            return Response({
                'total': 0,
                'correct': 0,
                'accuracy': 0,
                'by_confidence': {}
            })
        
        correct = analyses.filter(is_correct=True).count()
        
        # Estatísticas por nível de confiança
        by_confidence = {}
        for level in range(1, 6):
            level_analyses = analyses.filter(confidence=level)
            level_total = level_analyses.count()
            level_correct = level_analyses.filter(is_correct=True).count()
            
            by_confidence[level] = {
                'total': level_total,
                'correct': level_correct,
                'accuracy': round((level_correct / level_total * 100), 1) if level_total > 0 else 0
            }
        
        return Response({
            'total': total,
            'correct': correct,
            'accuracy': round((correct / total * 100), 1),
            'by_confidence': by_confidence
        })
```

---

### 5.4. Criar Views de Subscriptions

**Arquivo**: `backend/apps/subscriptions/views.py`

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Subscription, Payment
from .serializers import SubscriptionSerializer, PaymentSerializer, PaymentCreateSerializer
import uuid


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Assinaturas"""
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Assinatura atual ativa"""
        subscription = Subscription.objects.filter(
            user=request.user,
            status='active'
        ).first()
        
        if subscription:
            return Response(SubscriptionSerializer(subscription).data)
        
        return Response({
            'message': 'Nenhuma assinatura ativa',
            'is_premium': False
        }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar assinatura"""
        subscription = self.get_object()
        
        if subscription.user != request.user:
            return Response({
                'error': 'Não autorizado'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if subscription.status != 'active':
            return Response({
                'error': 'Assinatura não está ativa'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        subscription.cancel()
        
        return Response({
            'message': 'Assinatura cancelada com sucesso',
            'subscription': SubscriptionSerializer(subscription).data
        })


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Pagamentos"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def create_payment(self, request):
        """Iniciar pagamento M-Pesa"""
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        plan = serializer.validated_data['plan']
        phone_number = serializer.validated_data['phone_number']
        
        # Definir valores
        amounts = {
            'monthly': 499.00,
            'quarterly': 1299.00,
            'yearly': 4499.00
        }
        
        amount = amounts[plan]
        
        # Criar assinatura
        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            status='pending',
            amount_paid=amount
        )
        
        # Criar pagamento
        transaction_id = f"BET{uuid.uuid4().hex[:12].upper()}"
        
        payment = Payment.objects.create(
            user=request.user,
            subscription=subscription,
            amount=amount,
            phone_number=phone_number,
            transaction_id=transaction_id,
            status='pending'
        )
        
        # TODO: Integrar com M-Pesa API (Fase 6)
        # Por enquanto, simular sucesso
        
        return Response({
            'message': 'Pagamento iniciado. Verifique seu telefone para confirmar.',
            'payment': PaymentSerializer(payment).data,
            'instructions': 'Digite seu PIN M-Pesa quando solicitado'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        """Confirmar pagamento (webhook M-Pesa)"""
        payment = self.get_object()
        
        if payment.status == 'completed':
            return Response({
                'message': 'Pagamento já foi confirmado'
            })
        
        # TODO: Validar callback M-Pesa (Fase 6)
        
        payment.complete_payment()
        
        return Response({
            'message': 'Pagamento confirmado!',
            'payment': PaymentSerializer(payment).data
        })
```

---

### 5.5. Configurar URLs

**Arquivo**: `backend/apps/users/urls.py`

```python
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserProfileView, user_stats

urlpatterns = [
    # Autenticação JWT
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Perfil
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('stats/', user_stats, name='user-stats'),
]
```

**Arquivo**: `backend/config/urls.py`

```python
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.matches.views import LeagueViewSet, TeamViewSet, MatchViewSet
from apps.analysis.views import AnalysisViewSet
from apps.subscriptions.views import SubscriptionViewSet, PaymentViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r'leagues', LeagueViewSet, basename='league')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'matches', MatchViewSet, basename='match')
router.register(r'analyses', AnalysisViewSet, basename='analysis')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/', include(router.urls)),
]
```

---

## 🚀 FASE 6: INTEGRAÇÃO COM APIS EXTERNAS (Dia 7-9 - 12h)

### 6.1. Criar Serviço de Football Data

**Arquivo**: `backend/apps/matches/services/football_api.py`

```python
import requests
from django.conf import settings
from datetime import datetime, timedelta


class FootballDataService:
    """Serviço para Football-Data.org API"""
    
    BASE_URL = "https://api.football-data.org/v4"
    
    def __init__(self):
        self.api_key = settings.FOOTBALL_DATA_API_KEY
        self.headers = {'X-Auth-Token': self.api_key}
    
    def get_upcoming_matches(self, days=7):
        """Buscar partidas futuras"""
        date_from = datetime.now().strftime('%Y-%m-%d')
        date_to = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        url = f"{self.BASE_URL}/matches"
        params = {
            'dateFrom': date_from,
            'dateTo': date_to,
            'status': 'SCHEDULED'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar partidas: {e}")
            return None
    
    def get_match_details(self, match_id):
        """Buscar detalhes de uma partida"""
        url = f"{self.BASE_URL}/matches/{match_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar detalhes da partida: {e}")
            return None
    
    def get_team_stats(self, team_id):
        """Buscar estatísticas de um time"""
        url = f"{self.BASE_URL}/teams/{team_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar estatísticas do time: {e}")
            return None
    
    def get_h2h(self, team1_id, team2_id):
        """Buscar histórico entre dois times"""
        url = f"{self.BASE_URL}/matches"
        params = {
            'team1': team1_id,
            'team2': team2_id,
            'status': 'FINISHED'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar H2H: {e}")
            return None
```

---

### 6.2. Criar Serviço de Google Gemini AI

**Arquivo**: `backend/apps/analysis/services/ai_analyzer.py`

```python
import google.generativeai as genai
from django.conf import settings
import json


class AIAnalyzer:
    """Serviço de análise com Google Gemini"""
    
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def analyze_match(self, match_data):
        """
        Analisa uma partida e retorna predição
        
        match_data deve conter:
        - home_team: {'name': str, 'stats': dict}
        - away_team: {'name': str, 'stats': dict}
        - h2h: list de resultados anteriores
        - league: str
        - date: str
        """
        
        prompt = self._build_prompt(match_data)
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            return result
        except Exception as e:
            print(f"Erro na análise IA: {e}")
            return self._get_default_analysis()
    
    def _build_prompt(self, data):
        """Construir prompt para IA"""
        return f"""
Você é um especialista em análise de futebol. Analise a partida abaixo e forneça uma predição detalhada.

**PARTIDA:**
{data['home_team']['name']} vs {data['away_team']['name']}
Liga: {data.get('league', 'N/A')}
Data: {data.get('date', 'N/A')}

**ESTATÍSTICAS TIME DA CASA:**
{json.dumps(data['home_team'].get('stats', {}), indent=2)}

**ESTATÍSTICAS TIME VISITANTE:**
{json.dumps(data['away_team'].get('stats', {}), indent=2)}

**HISTÓRICO DIRETO (H2H):**
{json.dumps(data.get('h2h', []), indent=2)}

**INSTRUÇÕES:**
1. Analise forma recente, estatísticas, histórico direto
2. Considere fator casa, lesões, motivação
3. Calcule probabilidades para vitória casa, empate, vitória visitante
4. Forneça xG estimado para cada time
5. Defina confiança (1-5 estrelas)

**RESPONDA EM JSON:**
{{
    "prediction": "home|draw|away",
    "confidence": 1-5,
    "home_probability": 0-100,
    "draw_probability": 0-100,
    "away_probability": 0-100,
    "home_xg": 0-5,
    "away_xg": 0-5,
    "reasoning": "explicação detalhada",
    "key_factors": ["fator1", "fator2", "fator3"],
    "analysis_breakdown": {{
        "form": {{"home": 0-100, "away": 0-100}},
        "home_away": {{"advantage": 0-100}},
        "h2h": {{"score": 0-100}},
        "stats": {{"home": 0-100, "away": 0-100}}
    }}
}}
"""
    
    def _parse_response(self, response_text):
        """Parsear resposta da IA"""
        try:
            # Remover markdown se existir
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            result = json.loads(response_text.strip())
            
            # Validar campos obrigatórios
            required = ['prediction', 'confidence', 'home_probability', 
                       'draw_probability', 'away_probability', 'reasoning']
            
            for field in required:
                if field not in result:
                    raise ValueError(f"Campo {field} ausente")
            
            return result
            
        except Exception as e:
            print(f"Erro ao parsear resposta: {e}")
            return self._get_default_analysis()
    
    def _get_default_analysis(self):
        """Análise padrão em caso de erro"""
        return {
            'prediction': 'draw',
            'confidence': 2,
            'home_probability': 33.3,
            'draw_probability': 33.3,
            'away_probability': 33.4,
            'home_xg': 1.5,
            'away_xg': 1.5,
            'reasoning': 'Análise indisponível. Dados insuficientes.',
            'key_factors': ['Análise em modo seguro'],
            'analysis_breakdown': {}
        }
```

---

### 6.3. Criar Task Celery para Atualizar Partidas

**Arquivo**: `backend/apps/matches/tasks.py`

```python
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import League, Team, Match
from .services.football_api import FootballDataService


@shared_task
def fetch_upcoming_matches():
    """Buscar partidas futuras das APIs"""
    service = FootballDataService()
    data = service.get_upcoming_matches(days=7)
    
    if not data or 'matches' not in data:
        return {'error': 'Falha ao buscar partidas'}
    
    created = 0
    updated = 0
    
    for match_data in data['matches']:
        try:
            # Buscar ou criar liga
            league, _ = League.objects.get_or_create(
                football_data_id=match_data['competition']['id'],
                defaults={
                    'name': match_data['competition']['name'],
                    'country': match_data['area']['name'],
                    'logo': match_data['competition'].get('emblem', '')
                }
            )
            
            # Buscar ou criar times
            home_team, _ = Team.objects.get_or_create(
                football_data_id=match_data['homeTeam']['id'],
                defaults={
                    'name': match_data['homeTeam']['name'],
                    'logo': match_data['homeTeam'].get('crest', '')
                }
            )
            
            away_team, _ = Team.objects.get_or_create(
                football_data_id=match_data['awayTeam']['id'],
                defaults={
                    'name': match_data['awayTeam']['name'],
                    'logo': match_data['awayTeam'].get('crest', '')
                }
            )
            
            # Buscar ou criar partida
            match, was_created = Match.objects.update_or_create(
                football_data_id=match_data['id'],
                defaults={
                    'league': league,
                    'home_team': home_team,
                    'away_team': away_team,
                    'match_date': match_data['utcDate'],
                    'status': 'scheduled',
                    'home_score': match_data['score']['fullTime'].get('home'),
                    'away_score': match_data['score']['fullTime'].get('away'),
                }
            )
            
            if was_created:
                created += 1
            else:
                updated += 1
                
        except Exception as e:
            print(f"Erro ao processar partida: {e}")
            continue
    
    return {
        'created': created,
        'updated': updated,
        'total': created + updated
    }


@shared_task
def update_finished_matches():
    """Atualizar placares de partidas finalizadas"""
    service = FootballDataService()
    
    # Buscar partidas que deveriam ter terminado
    yesterday = timezone.now() - timedelta(days=1)
    matches = Match.objects.filter(
        match_date__lt=yesterday,
        status__in=['scheduled', 'live']
    )
    
    updated = 0
    
    for match in matches:
        if match.football_data_id:
            data = service.get_match_details(match.football_data_id)
            
            if data and data.get('status') == 'FINISHED':
                match.status = 'finished'
                match.home_score = data['score']['fullTime']['home']
                match.away_score = data['score']['fullTime']['away']
                match.save()
                
                # Validar análises desta partida
                for analysis in match.analyses.all():
                    analysis.validate_result()
                
                updated += 1
    
    return {'updated': updated}
```

**Arquivo**: `backend/config/celery.py`

```python
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Agendar tasks
app.conf.beat_schedule = {
    'fetch-matches-every-6-hours': {
        'task': 'apps.matches.tasks.fetch_upcoming_matches',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    'update-finished-matches-daily': {
        'task': 'apps.matches.tasks.update_finished_matches',
        'schedule': crontab(minute=0, hour=1),
    },
}
```

**Arquivo**: `backend/config/__init__.py`

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

---

## 📝 COMANDOS PARA TESTAR

### Instalar dependências adicionais:
```bash
pip install google-generativeai celery redis django-filter
pip freeze > requirements.txt
```

### Iniciar Celery Worker:
```bash
celery -A config worker -l info
```

### Iniciar Celery Beat (agendador):
```bash
celery -A config beat -l info
```

### Testar endpoints com curl:

**Registro:**
```bash
curl -X POST http://localhost:8000/api/users/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","username":"user","password":"Test@123","password2":"Test@123"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"Test@123"}'
```

**Listar Partidas:**
```bash
curl -X GET http://localhost:8000/api/matches/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

**Solicitar Análise:**
```bash
curl -X POST http://localhost:8000/api/analyses/request_analysis/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"match_id":1}'
```

---

## 🚀 PRÓXIMAS FASES (Resumo)

**Fase 7-10: Frontend React PWA (Dias 10-20)**
- Setup React + Vite + Tailwind
- Sistema de autenticação
- Interface de listagem de partidas
- Tela de análise detalhada
- PWA (Service Workers, offline mode)
- Push notifications

**Fase 11-12: Pagamentos e Premium (Dias 21-24)**
- Integração M-Pesa completa
- Fluxo de assinatura
- Gestão de premium

**Fase 13-14: Testes e Otimização (Dias 25-27)**
- Testes unitários e integração
- Performance e caching
- SEO e otimizações

**Fase 15: Deploy (Dia 28)**
- Deploy backend (Railway/Heroku)
- Deploy frontend (Vercel)
- Configuração domínio
- Monitoramento

---

## ✅ CHECKLIST FASE 4-6

- [ ] Criar todos os serializers
- [ ] Implementar views e viewsets
- [ ] Configurar URLs e routers
- [ ] Testar todos endpoints com Postman/curl
- [ ] Implementar serviço Football API
- [ ] Implementar serviço Gemini AI
- [ ] Configurar Celery e Redis
- [ ] Criar tasks de atualização
- [ ] Testar integração completa
- [ ] Documentar APIs (opcional: Swagger/OpenAPI)

**Tempo estimado Fases 4-6:** 28 horas
**Resultado esperado:** Backend REST API completo e funcional com IA
