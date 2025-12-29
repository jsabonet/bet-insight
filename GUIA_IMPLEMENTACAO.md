# 🏗️ GUIA DE IMPLEMENTAÇÃO - BET INSIGHT MOZAMBIQUE
## Backend Django + PostgreSQL | Frontend Next.js PWA

---

## 📋 ÍNDICE

1. [Visão Geral da Arquitetura](#visão-geral-da-arquitetura)
2. [Setup do Ambiente](#setup-do-ambiente)
3. [Backend Django](#backend-django)
4. [Frontend Next.js PWA](#frontend-nextjs-pwa)
5. [Integrações](#integrações)
6. [Deploy](#deploy)
7. [Testes](#testes)

---

## 🏛️ VISÃO GERAL DA ARQUITETURA

```
┌─────────────────────────────────────────────────────────────┐
│                        USUÁRIOS                             │
│          (Mobile Browser / Desktop / PWA Instalado)         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ HTTPS
                  │
┌─────────────────▼───────────────────────────────────────────┐
│              FRONTEND - Next.js 14 PWA                      │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │ Landing  │Dashboard │ Análise  │Histórico │  Auth    │  │
│  │  Page    │  (Jogos) │   (IA)   │  Stats   │ (Login)  │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
│                                                             │
│  - Tailwind CSS + Shadcn/ui                                │
│  - Service Worker (Offline)                                │
│  - Push Notifications (FCM)                                │
│  - PWA Installable                                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ REST API (JSON)
                  │
┌─────────────────▼───────────────────────────────────────────┐
│            BACKEND - Django REST Framework                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Django Apps                             │  │
│  ├──────────┬──────────┬──────────┬───────────────────┐ │  │
│  │  Users   │ Matches  │ Analysis │  Subscriptions    │ │  │
│  │  (Auth)  │ (Jogos)  │  (IA)    │   (Pagamentos)    │ │  │
│  └──────────┴──────────┴──────────┴───────────────────┘ │  │
│  │                                                       │  │
│  │  ┌─────────────────────────────────────────────┐    │  │
│  │  │         API Endpoints                       │    │  │
│  │  ├─────────────────────────────────────────────┤    │  │
│  │  │ /api/auth/                                  │    │  │
│  │  │ /api/matches/                               │    │  │
│  │  │ /api/analysis/                              │    │  │
│  │  │ /api/subscriptions/                         │    │  │
│  │  │ /api/webhook/mpesa/                         │    │  │
│  │  └─────────────────────────────────────────────┘    │  │
│  │                                                       │  │
│  │  - Django REST Framework                             │  │
│  │  - JWT Authentication                                │  │
│  │  - Celery (Tasks Assíncronas)                       │  │
│  │  - Redis (Cache & Queue)                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┬──────────────┐
        │                   │              │
┌───────▼────────┐  ┌──────▼──────┐  ┌───▼────────┐
│   PostgreSQL   │  │    Redis    │  │  Celery    │
│   (Database)   │  │   (Cache)   │  │  Worker    │
└────────────────┘  └─────────────┘  └────────────┘
        │
        │ SQL
        │
┌───────▼─────────────────────────────────────────────────────┐
│                  EXTERNAL SERVICES                          │
│  ┌──────────┬──────────────┬────────────┬────────────────┐ │
│  │  Gemini  │  Football    │   M-Pesa   │   Firebase     │ │
│  │   API    │  Data APIs   │    API     │  (Push/FCM)    │ │
│  │  (IA)    │ (Estatísticas│(Pagamento) │ (Notificações) │ │
│  └──────────┴──────────────┴────────────┴────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 SETUP DO AMBIENTE

### Pré-requisitos

```bash
# Software necessário
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Git
```

### 1. Clonar Repositório

```bash
# Criar estrutura de pastas
mkdir bet-insight-mozambique
cd bet-insight-mozambique

# Estrutura
bet-insight-mozambique/
├── backend/          # Django
├── frontend/         # Next.js PWA
└── docker/           # Docker configs
```

---

## 🐍 BACKEND DJANGO

### Estrutura do Backend

```
backend/
├── config/                      # Configurações Django
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py             # Settings base
│   │   ├── development.py      # Dev settings
│   │   └── production.py       # Prod settings
│   ├── urls.py                 # URLs principais
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── users/                  # App de usuários
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── admin.py
│   ├── matches/                # App de jogos
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services.py        # Lógica de negócio
│   ├── analysis/               # App de análises
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── ai_service.py      # Integração Gemini
│   └── subscriptions/          # App de assinaturas
│       ├── migrations/
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       └── mpesa_service.py   # Integração M-Pesa
├── core/                       # Utils compartilhados
│   ├── __init__.py
│   ├── permissions.py
│   ├── pagination.py
│   └── exceptions.py
├── tasks/                      # Celery tasks
│   ├── __init__.py
│   ├── celery.py
│   └── scheduled_tasks.py
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── manage.py
├── .env.example
└── pytest.ini
```

### 1. Setup Inicial Django

```bash
# Criar e ativar ambiente virtual
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Instalar Django e dependências
pip install django djangorestframework
pip install psycopg2-binary python-decouple
pip install django-cors-headers djangorestframework-simplejwt
pip install celery redis
pip install google-generativeai requests
pip install pillow

# Criar projeto Django
django-admin startproject config .

# Criar apps
python manage.py startapp users
python manage.py startapp matches
python manage.py startapp analysis
python manage.py startapp subscriptions

# Mover apps para pasta apps/
mkdir apps
mv users matches analysis subscriptions apps/
```

### 2. Configuração PostgreSQL

```python
# config/settings/base.py

from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    
    # Local apps
    'apps.users',
    'apps.matches',
    'apps.analysis',
    'apps.subscriptions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='betinsight_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CORS
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://betinsight.co.mz',
]

# Celery
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# APIs Keys
GEMINI_API_KEY = config('GEMINI_API_KEY')
FOOTBALL_API_KEY = config('FOOTBALL_API_KEY')
MPESA_API_KEY = config('MPESA_API_KEY')
FIREBASE_SERVER_KEY = config('FIREBASE_SERVER_KEY')

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'Africa/Maputo'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 3. Models (Banco de Dados)

#### 3.1 User Model

```python
# apps/users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Modelo customizado de usuário"""
    
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(_('telefone'), max_length=20, unique=True)
    
    # Créditos de análise
    daily_analysis_count = models.IntegerField(
        _('análises diárias usadas'),
        default=0
    )
    daily_analysis_limit = models.IntegerField(
        _('limite de análises diárias'),
        default=5
    )
    
    # Assinatura
    is_premium = models.BooleanField(_('é premium'), default=False)
    premium_until = models.DateTimeField(
        _('premium até'),
        null=True,
        blank=True
    )
    
    # Push notifications
    fcm_token = models.CharField(
        _('FCM token'),
        max_length=255,
        blank=True,
        null=True
    )
    notifications_enabled = models.BooleanField(
        _('notificações ativadas'),
        default=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']
    
    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    def reset_daily_analysis_count(self):
        """Reseta contador diário de análises"""
        self.daily_analysis_count = 0
        self.save()
    
    def can_analyze(self):
        """Verifica se usuário pode fazer análise"""
        if self.is_premium:
            return True
        return self.daily_analysis_count < self.daily_analysis_limit
    
    def increment_analysis_count(self):
        """Incrementa contador de análises"""
        self.daily_analysis_count += 1
        self.save()
```

#### 3.2 Match Model

```python
# apps/matches/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class League(models.Model):
    """Modelo de Liga/Competição"""
    
    name = models.CharField(_('nome'), max_length=100)
    country = models.CharField(_('país'), max_length=50)
    api_id = models.IntegerField(_('ID da API'), unique=True)
    logo = models.URLField(_('logo'), blank=True)
    is_active = models.BooleanField(_('ativo'), default=True)
    
    class Meta:
        verbose_name = _('liga')
        verbose_name_plural = _('ligas')
    
    def __str__(self):
        return self.name


class Team(models.Model):
    """Modelo de Time"""
    
    name = models.CharField(_('nome'), max_length=100)
    api_id = models.IntegerField(_('ID da API'), unique=True)
    logo = models.URLField(_('logo'), blank=True)
    
    class Meta:
        verbose_name = _('time')
        verbose_name_plural = _('times')
    
    def __str__(self):
        return self.name


class Match(models.Model):
    """Modelo de Jogo"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Agendado'),
        ('live', 'Ao Vivo'),
        ('finished', 'Finalizado'),
        ('postponed', 'Adiado'),
        ('cancelled', 'Cancelado'),
    ]
    
    # Informações básicas
    api_id = models.IntegerField(_('ID da API'), unique=True)
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name='matches',
        verbose_name=_('liga')
    )
    home_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='home_matches',
        verbose_name=_('time casa')
    )
    away_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='away_matches',
        verbose_name=_('time visitante')
    )
    
    # Data e status
    match_date = models.DateTimeField(_('data do jogo'))
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    
    # Resultado
    home_score = models.IntegerField(_('gols casa'), null=True, blank=True)
    away_score = models.IntegerField(_('gols fora'), null=True, blank=True)
    
    # Metadados
    venue = models.CharField(_('estádio'), max_length=100, blank=True)
    referee = models.CharField(_('árbitro'), max_length=100, blank=True)
    round = models.CharField(_('rodada'), max_length=50, blank=True)
    season = models.CharField(_('temporada'), max_length=20)
    
    # Cache de estatísticas (JSON)
    stats_cache = models.JSONField(_('cache de estatísticas'), null=True, blank=True)
    last_stats_update = models.DateTimeField(_('última atualização stats'), null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('jogo')
        verbose_name_plural = _('jogos')
        ordering = ['match_date']
        indexes = [
            models.Index(fields=['match_date', 'status']),
            models.Index(fields=['league', 'match_date']),
        ]
    
    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.match_date.strftime('%d/%m/%Y')}"
```

#### 3.3 Analysis Model

```python
# apps/analysis/models.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Analysis(models.Model):
    """Modelo de Análise com IA"""
    
    # Relacionamentos
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analyses',
        verbose_name=_('usuário')
    )
    match = models.ForeignKey(
        'matches.Match',
        on_delete=models.CASCADE,
        related_name='analyses',
        verbose_name=_('jogo')
    )
    
    # Previsão
    home_probability = models.DecimalField(
        _('probabilidade casa'),
        max_digits=5,
        decimal_places=2
    )
    draw_probability = models.DecimalField(
        _('probabilidade empate'),
        max_digits=5,
        decimal_places=2
    )
    away_probability = models.DecimalField(
        _('probabilidade fora'),
        max_digits=5,
        decimal_places=2
    )
    
    # Recomendação
    recommendation = models.CharField(
        _('recomendação'),
        max_length=255
    )
    alternative_recommendation = models.CharField(
        _('recomendação alternativa'),
        max_length=255,
        blank=True
    )
    
    # Confiança
    confidence = models.IntegerField(
        _('confiança'),
        choices=[(i, f'{i} estrelas') for i in range(1, 6)]
    )
    
    # Análise detalhada (JSON)
    reasoning = models.TextField(_('raciocínio'))
    key_factors = models.JSONField(_('fatores-chave'))
    risk_factors = models.JSONField(_('fatores de risco'))
    expected_goals = models.JSONField(_('gols esperados'))
    detailed_bets = models.JSONField(_('apostas detalhadas'), null=True, blank=True)
    
    # Dados usados na análise
    analysis_data = models.JSONField(_('dados da análise'))
    
    # Validação (após jogo)
    is_validated = models.BooleanField(_('validado'), default=False)
    was_correct = models.BooleanField(_('estava correto'), null=True, blank=True)
    actual_result = models.CharField(
        _('resultado real'),
        max_length=10,
        blank=True,
        choices=[('1', 'Casa'), ('X', 'Empate'), ('2', 'Fora')]
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('análise')
        verbose_name_plural = _('análises')
        ordering = ['-created_at']
        unique_together = ['user', 'match']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['match', '-created_at']),
        ]
    
    def __str__(self):
        return f"Análise de {self.user} - {self.match}"
    
    def validate_prediction(self):
        """Valida previsão após jogo finalizado"""
        if self.match.status != 'finished':
            return
        
        # Determinar resultado real
        if self.match.home_score > self.match.away_score:
            actual = '1'
        elif self.match.home_score < self.match.away_score:
            actual = '2'
        else:
            actual = 'X'
        
        self.actual_result = actual
        
        # Verificar se previsão estava correta
        predicted = max(
            [('1', self.home_probability), 
             ('X', self.draw_probability), 
             ('2', self.away_probability)],
            key=lambda x: x[1]
        )[0]
        
        self.was_correct = (predicted == actual)
        self.is_validated = True
        self.save()
```

#### 3.4 Subscription Model

```python
# apps/subscriptions/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Subscription(models.Model):
    """Modelo de Assinatura"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('active', 'Ativo'),
        ('expired', 'Expirado'),
        ('cancelled', 'Cancelado'),
    ]
    
    # Relacionamento
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name=_('usuário')
    )
    
    # Período
    start_date = models.DateTimeField(_('data início'))
    end_date = models.DateTimeField(_('data fim'))
    
    # Status e pagamento
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    amount = models.DecimalField(
        _('valor'),
        max_digits=10,
        decimal_places=2
    )
    currency = models.CharField(
        _('moeda'),
        max_length=3,
        default='MZN'
    )
    
    # Pagamento M-Pesa
    payment_method = models.CharField(
        _('método de pagamento'),
        max_length=50,
        default='mpesa'
    )
    payment_reference = models.CharField(
        _('referência de pagamento'),
        max_length=100,
        blank=True
    )
    payment_proof = models.ImageField(
        _('comprovante'),
        upload_to='payment_proofs/',
        null=True,
        blank=True
    )
    
    # Auto-renovação
    auto_renew = models.BooleanField(_('renovação automática'), default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('assinatura')
        verbose_name_plural = _('assinaturas')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Assinatura de {self.user} - {self.status}"
    
    def is_active(self):
        """Verifica se assinatura está ativa"""
        return (
            self.status == 'active' and
            self.end_date > timezone.now()
        )
    
    def activate(self):
        """Ativa assinatura"""
        self.status = 'active'
        self.user.is_premium = True
        self.user.premium_until = self.end_date
        self.user.save()
        self.save()
    
    def expire(self):
        """Expira assinatura"""
        self.status = 'expired'
        self.user.is_premium = False
        self.user.premium_until = None
        self.user.save()
        self.save()


class Payment(models.Model):
    """Modelo de Pagamento"""
    
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('assinatura')
    )
    
    amount = models.DecimalField(_('valor'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('moeda'), max_length=3, default='MZN')
    
    # M-Pesa
    mpesa_transaction_id = models.CharField(
        _('ID transação M-Pesa'),
        max_length=100,
        unique=True
    )
    mpesa_phone = models.CharField(_('telefone M-Pesa'), max_length=20)
    
    # Status
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=[
            ('pending', 'Pendente'),
            ('completed', 'Completo'),
            ('failed', 'Falhou'),
        ],
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('pagamento')
        verbose_name_plural = _('pagamentos')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pagamento {self.mpesa_transaction_id} - {self.status}"
```

### 4. Serializers

```python
# apps/users/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'phone', 
            'is_premium', 'premium_until',
            'daily_analysis_count', 'daily_analysis_limit',
            'notifications_enabled', 'created_at'
        ]
        read_only_fields = ['id', 'is_premium', 'premium_until', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'phone', 'password', 'password_confirm']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Senhas não conferem")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user
```

```python
# apps/matches/serializers.py

from rest_framework import serializers
from .models import Match, League, Team

class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = ['id', 'name', 'country', 'logo', 'is_active']


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'logo']


class MatchSerializer(serializers.ModelSerializer):
    league = LeagueSerializer(read_only=True)
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)
    has_analysis = serializers.SerializerMethodField()
    
    class Meta:
        model = Match
        fields = [
            'id', 'api_id', 'league', 'home_team', 'away_team',
            'match_date', 'status', 'home_score', 'away_score',
            'venue', 'referee', 'round', 'season',
            'has_analysis', 'created_at'
        ]
    
    def get_has_analysis(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.analyses.filter(user=request.user).exists()
        return False
```

```python
# apps/analysis/serializers.py

from rest_framework import serializers
from .models import Analysis
from apps.matches.serializers import MatchSerializer

class AnalysisSerializer(serializers.ModelSerializer):
    match = MatchSerializer(read_only=True)
    
    class Meta:
        model = Analysis
        fields = [
            'id', 'match', 'home_probability', 'draw_probability', 
            'away_probability', 'recommendation', 'alternative_recommendation',
            'confidence', 'reasoning', 'key_factors', 'risk_factors',
            'expected_goals', 'detailed_bets', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
```

### 5. Views (API Endpoints)

```python
# apps/users/views.py

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserRegistrationSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """Registro de novo usuário"""
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
            }
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Perfil do usuário"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_fcm_token(request):
    """Atualizar FCM token para push notifications"""
    token = request.data.get('fcm_token')
    if token:
        request.user.fcm_token = token
        request.user.save()
        return Response({'message': 'FCM token atualizado'})
    return Response(
        {'error': 'Token não fornecido'},
        status=status.HTTP_400_BAD_REQUEST
    )
```

```python
# apps/matches/views.py

from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import Match, League
from .serializers import MatchSerializer, LeagueSerializer

class MatchListView(generics.ListAPIView):
    """Lista de jogos"""
    permission_classes = [IsAuthenticated]
    serializer_class = MatchSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['home_team__name', 'away_team__name']
    ordering_fields = ['match_date']
    ordering = ['match_date']
    
    def get_queryset(self):
        queryset = Match.objects.select_related(
            'league', 'home_team', 'away_team'
        ).filter(status='scheduled')
        
        # Filtrar por data (próximas 48h por padrão)
        days = int(self.request.query_params.get('days', 2))
        end_date = timezone.now() + timedelta(days=days)
        queryset = queryset.filter(
            match_date__gte=timezone.now(),
            match_date__lte=end_date
        )
        
        # Filtrar por liga
        league_id = self.request.query_params.get('league')
        if league_id:
            queryset = queryset.filter(league_id=league_id)
        
        return queryset


class MatchDetailView(generics.RetrieveAPIView):
    """Detalhes de um jogo"""
    permission_classes = [IsAuthenticated]
    serializer_class = MatchSerializer
    queryset = Match.objects.select_related('league', 'home_team', 'away_team')


class LeagueListView(generics.ListAPIView):
    """Lista de ligas"""
    permission_classes = [IsAuthenticated]
    serializer_class = LeagueSerializer
    queryset = League.objects.filter(is_active=True)
```

```python
# apps/analysis/views.py

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Analysis
from .serializers import AnalysisSerializer
from apps.matches.models import Match
from .ai_service import generate_analysis

class AnalysisListView(generics.ListAPIView):
    """Lista de análises do usuário"""
    permission_classes = [IsAuthenticated]
    serializer_class = AnalysisSerializer
    
    def get_queryset(self):
        return Analysis.objects.filter(
            user=self.request.user
        ).select_related('match', 'match__league', 'match__home_team', 'match__away_team')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_analysis(request, match_id):
    """Criar análise para um jogo"""
    user = request.user
    
    # Verificar se pode analisar
    if not user.can_analyze():
        return Response(
            {
                'error': 'Limite de análises diárias atingido',
                'limit': user.daily_analysis_limit,
                'used': user.daily_analysis_count
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Buscar jogo
    match = get_object_or_404(Match, id=match_id)
    
    # Verificar se já analisou este jogo
    if Analysis.objects.filter(user=user, match=match).exists():
        return Response(
            {'error': 'Você já analisou este jogo'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Gerar análise com IA
    try:
        analysis_data = generate_analysis(match)
        
        # Criar análise
        analysis = Analysis.objects.create(
            user=user,
            match=match,
            home_probability=analysis_data['prediction']['home'],
            draw_probability=analysis_data['prediction']['draw'],
            away_probability=analysis_data['prediction']['away'],
            recommendation=analysis_data['recommendation'],
            alternative_recommendation=analysis_data.get('alternative_recommendation', ''),
            confidence=analysis_data['confidence'],
            reasoning=analysis_data['reasoning'],
            key_factors=analysis_data['key_factors'],
            risk_factors=analysis_data['risk_factors'],
            expected_goals=analysis_data['expected_goals'],
            detailed_bets=analysis_data.get('detailed_bets'),
            analysis_data=analysis_data
        )
        
        # Incrementar contador
        user.increment_analysis_count()
        
        serializer = AnalysisSerializer(analysis)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Erro ao gerar análise: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class AnalysisDetailView(generics.RetrieveAPIView):
    """Detalhes de uma análise"""
    permission_classes = [IsAuthenticated]
    serializer_class = AnalysisSerializer
    
    def get_queryset(self):
        return Analysis.objects.filter(user=self.request.user)
```

### 6. Serviços Externos

#### 6.1 Serviço Gemini IA

```python
# apps/analysis/ai_service.py

import google.generativeai as genai
from django.conf import settings
from apps.matches.models import Match

# Configurar Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_analysis(match: Match) -> dict:
    """Gera análise com IA usando Google Gemini"""
    
    # Coletar dados do jogo
    match_data = collect_match_data(match)
    
    # Criar prompt
    prompt = build_analysis_prompt(match_data)
    
    # Chamar Gemini
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(prompt)
    
    # Extrair JSON da resposta
    import json
    import re
    
    text = response.text
    json_match = re.search(r'\{[\s\S]*\}', text)
    
    if not json_match:
        raise ValueError("IA não retornou JSON válido")
    
    analysis = json.loads(json_match.group())
    
    return analysis


def collect_match_data(match: Match) -> dict:
    """Coleta dados necessários para análise"""
    # Aqui você buscaria dados das APIs de futebol
    # Por enquanto, dados mockados
    
    return {
        'home_team': match.home_team.name,
        'away_team': match.away_team.name,
        'league': match.league.name,
        'match_date': match.match_date.isoformat(),
        # ... adicionar dados reais das APIs
    }


def build_analysis_prompt(data: dict) -> str:
    """Constrói prompt para Gemini"""
    
    prompt = f"""
Você é um especialista em análise de apostas de futebol.

JOGO: {data['home_team']} vs {data['away_team']}
LIGA: {data['league']}

Analise e retorne APENAS JSON:

{{
  "prediction": {{"home": 35, "draw": 25, "away": 40}},
  "recommendation": "Apostar em ...",
  "alternative_recommendation": "Over 2.5 gols",
  "confidence": 4,
  "reasoning": "...",
  "key_factors": ["fator1", "fator2"],
  "risk_factors": ["risco1"],
  "expected_goals": {{"home": 1.2, "away": 2.1, "total": 3.3}},
  "detailed_bets": [
    {{"market": "1X2", "bet": "...", "probability": 40, "confidence": 4}}
  ]
}}
"""
    
    return prompt
```

#### 6.2 Serviço M-Pesa

```python
# apps/subscriptions/mpesa_service.py

import requests
from django.conf import settings

class MPesaService:
    """Serviço de integração com M-Pesa"""
    
    def __init__(self):
        self.api_key = settings.MPESA_API_KEY
        self.base_url = 'https://api.mpesa.vm.co.mz'
    
    def initiate_payment(self, phone: str, amount: float, reference: str):
        """Iniciar pagamento M-Pesa"""
        
        url = f'{self.base_url}/c2b/v1/payment'
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'phone': phone,
            'amount': amount,
            'reference': reference,
            'description': 'Assinatura Bet Insight Premium'
        }
        
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def verify_payment(self, transaction_id: str):
        """Verificar status de pagamento"""
        
        url = f'{self.base_url}/c2b/v1/payment/{transaction_id}'
        
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()
```

### 7. Celery Tasks

```python
# tasks/celery.py

from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('betinsight')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

```python
# tasks/scheduled_tasks.py

from celery import shared_task
from django.utils import timezone
from apps.users.models import User
from apps.subscriptions.models import Subscription
from apps.analysis.models import Analysis

@shared_task
def reset_daily_analysis_counts():
    """Reseta contadores diários de análise (roda todo dia à meia-noite)"""
    User.objects.all().update(daily_analysis_count=0)
    return "Daily analysis counts reset"


@shared_task
def check_expired_subscriptions():
    """Verifica e expira assinaturas vencidas"""
    expired = Subscription.objects.filter(
        status='active',
        end_date__lt=timezone.now()
    )
    
    for subscription in expired:
        subscription.expire()
    
    return f"{expired.count()} subscriptions expired"


@shared_task
def validate_predictions():
    """Valida previsões após jogos finalizados"""
    analyses = Analysis.objects.filter(
        is_validated=False,
        match__status='finished'
    )
    
    for analysis in analyses:
        analysis.validate_prediction()
    
    return f"{analyses.count()} predictions validated"


@shared_task
def fetch_today_matches():
    """Busca jogos do dia das APIs de futebol"""
    from apps.matches.services import FootballAPIService
    
    service = FootballAPIService()
    matches = service.fetch_today_matches()
    
    return f"{len(matches)} matches fetched"
```

### 8. URLs

```python
# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/matches/', include('apps.matches.urls')),
    path('api/analysis/', include('apps.analysis.urls')),
    path('api/subscriptions/', include('apps.subscriptions.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

```python
# apps/users/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('fcm-token/', views.update_fcm_token, name='update_fcm_token'),
]
```

```python
# apps/matches/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.MatchListView.as_view(), name='match_list'),
    path('<int:pk>/', views.MatchDetailView.as_view(), name='match_detail'),
    path('leagues/', views.LeagueListView.as_view(), name='league_list'),
]
```

```python
# apps/analysis/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.AnalysisListView.as_view(), name='analysis_list'),
    path('<int:pk>/', views.AnalysisDetailView.as_view(), name='analysis_detail'),
    path('create/<int:match_id>/', views.create_analysis, name='create_analysis'),
]
```

### 9. Admin

```python
# apps/users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'is_premium', 'premium_until', 'created_at']
    list_filter = ['is_premium', 'is_staff', 'created_at']
    search_fields = ['email', 'username', 'phone']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('phone', 'is_premium', 'premium_until', 
                      'daily_analysis_count', 'daily_analysis_limit',
                      'fcm_token', 'notifications_enabled')
        }),
    )
```

```python
# apps/matches/admin.py

from django.contrib import admin
from .models import League, Team, Match

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'is_active']
    list_filter = ['is_active', 'country']
    search_fields = ['name']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'league', 'match_date', 'status']
    list_filter = ['status', 'league', 'match_date']
    search_fields = ['home_team__name', 'away_team__name']
    date_hierarchy = 'match_date'
```

### 10. Arquivo .env

```bash
# .env.example

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=betinsight_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379

# APIs
GEMINI_API_KEY=your-gemini-key
FOOTBALL_API_KEY=your-football-api-key
MPESA_API_KEY=your-mpesa-key
FIREBASE_SERVER_KEY=your-firebase-key

# URLs
FRONTEND_URL=http://localhost:3000
```

### 11. Requirements

```txt
# requirements/base.txt

Django==5.0.1
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
django-redis==5.4.0

# Database
psycopg2-binary==2.9.9

# Celery
celery==5.3.6
redis==5.0.1

# APIs
google-generativeai==0.3.2
requests==2.31.0

# Utils
python-decouple==3.8
Pillow==10.2.0
python-dateutil==2.8.2

# Production
gunicorn==21.2.0
whitenoise==6.6.0
```

### 12. Comandos para Setup

```bash
# 1. Criar banco de dados PostgreSQL
createdb betinsight_db

# 2. Aplicar migrations
python manage.py makemigrations
python manage.py migrate

# 3. Criar superusuário
python manage.py createsuperuser

# 4. Coletar arquivos estáticos
python manage.py collectstatic

# 5. Rodar servidor
python manage.py runserver

# 6. Rodar Celery (em outro terminal)
celery -A tasks worker -l info

# 7. Rodar Celery Beat (tarefas agendadas)
celery -A tasks beat -l info
```

---

## 🎨 FRONTEND NEXT.JS PWA

*Continuo na próxima parte...*

Quer que eu continue com a parte do Frontend Next.js PWA e integrações?
