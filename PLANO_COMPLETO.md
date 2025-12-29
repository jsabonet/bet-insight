# 🚀 PLANO DE IMPLEMENTAÇÃO COMPLETO
## Bet Insight Mozambique - Do Zero ao Deploy
### Backend: Django + PostgreSQL | Frontend: React PWA

---

## 📑 ESTRUTURA DO PLANO

Este documento detalha TODOS os passos para construir a plataforma completa, do início ao fim.
Cada fase pode ser implementada sequencialmente, testada e validada antes de avançar.

---

## 🗂️ VISÃO GERAL DAS FASES

```
FASE 1: Setup do Ambiente (Dia 1)
├─ Instalar ferramentas necessárias
├─ Configurar PostgreSQL
├─ Criar estrutura de pastas
└─ Inicializar Git

FASE 2: Backend Django - Fundação (Dias 2-3)
├─ Criar projeto Django
├─ Configurar PostgreSQL
├─ Criar modelo User customizado
├─ Configurar Django REST Framework
└─ Implementar autenticação JWT

FASE 3: Backend - Models e Database (Dias 4-5)
├─ Criar modelo Match
├─ Criar modelo Analysis
├─ Criar modelo Subscription
├─ Migrations e testes
└─ Popular banco com dados de teste

FASE 4: Backend - API Endpoints (Dias 6-8)
├─ API de autenticação
├─ API de jogos
├─ API de análises
├─ API de assinaturas
└─ Testes de endpoints

FASE 5: Backend - Integrações Externas (Dias 9-10)
├─ Integração Football APIs
├─ Integração Google Gemini IA
├─ Integração M-Pesa
└─ Testes de integrações

FASE 6: Backend - Tasks e Jobs (Dia 11)
├─ Configurar Celery + Redis
├─ Tasks de atualização de jogos
├─ Tasks de validação de previsões
└─ Tasks de expiração de assinaturas

FASE 7: Frontend React - Fundação (Dias 12-13)
├─ Criar projeto React
├─ Configurar Tailwind CSS
├─ Setup de rotas (React Router)
├─ Configurar Axios
└─ Context API para estado global

FASE 8: Frontend - Autenticação (Dia 14)
├─ Tela de Login
├─ Tela de Registro
├─ Tela de Recuperação de senha
├─ Gerenciamento de tokens
└─ Rotas protegidas

FASE 9: Frontend - Dashboard (Dias 15-16)
├─ Header e navegação
├─ Lista de jogos
├─ Filtros e busca
├─ Cards de jogos
└─ Loading states

FASE 10: Frontend - Análise com IA (Dias 17-18)
├─ Página de análise detalhada
├─ Gráficos de probabilidade
├─ Exibição de recomendações
├─ Estatísticas do jogo
└─ Botão de análise

FASE 11: Frontend - Assinatura e Pagamento (Dia 19)
├─ Página de planos
├─ Fluxo de pagamento M-Pesa
├─ Upload de comprovante
└─ Gestão de assinatura

FASE 12: Frontend - PWA Setup (Dia 20)
├─ Service Worker
├─ Manifest.json
├─ Offline mode
├─ Install prompt
└─ Push notifications

FASE 13: Testes e Qualidade (Dias 21-22)
├─ Testes backend (Pytest)
├─ Testes frontend (Jest)
├─ Testes de integração
└─ Correção de bugs

FASE 14: Deploy e Produção (Dias 23-25)
├─ Deploy backend (Railway/Heroku)
├─ Deploy frontend (Vercel/Netlify)
├─ Configurar domínio
├─ SSL e segurança
└─ Monitoramento

FASE 15: Lançamento e Marketing (Dias 26-28)
├─ Beta testing
├─ Coleta de feedback
├─ Ajustes finais
└─ Lançamento público
```

---

# 📋 FASE 1: SETUP DO AMBIENTE

## Objetivo
Preparar o ambiente de desenvolvimento com todas as ferramentas necessárias.

## Checklist
- [ ] Instalar Python 3.11+
- [ ] Instalar Node.js 20+
- [ ] Instalar PostgreSQL 15+
- [ ] Instalar Redis
- [ ] Instalar VS Code
- [ ] Instalar Git

---

## PASSO 1.1: Instalar Python

### Windows
```powershell
# Baixar Python 3.11+ de python.org
# Ou usar winget
winget install Python.Python.3.11

# Verificar instalação
python --version
pip --version
```

### Verificação
```powershell
python --version
# Output esperado: Python 3.11.x
```

---

## PASSO 1.2: Instalar Node.js

### Windows
```powershell
# Baixar de nodejs.org
# Ou usar winget
winget install OpenJS.NodeJS

# Verificar instalação
node --version
npm --version
```

### Verificação
```powershell
node --version
# Output esperado: v20.x.x

npm --version
# Output esperado: 10.x.x
```

---

## PASSO 1.3: Instalar PostgreSQL

### Windows
```powershell
# Baixar PostgreSQL de postgresql.org
# Ou usar winget
winget install PostgreSQL.PostgreSQL

# Durante instalação:
# - Definir senha do usuário postgres
# - Anotar a senha (importante!)
# - Porta padrão: 5432
```

### Verificação
```powershell
# Abrir pgAdmin 4 (instalado com PostgreSQL)
# Conectar ao servidor local
# Criar banco de dados "betinsight_db"
```

### Criar Database via Terminal
```powershell
# Conectar ao PostgreSQL
psql -U postgres

# Dentro do psql:
CREATE DATABASE betinsight_db;
CREATE USER betinsight_user WITH PASSWORD 'senha_forte_aqui';
GRANT ALL PRIVILEGES ON DATABASE betinsight_db TO betinsight_user;
\q
```

---

## PASSO 1.4: Instalar Redis

### Windows
```powershell
# Opção 1: Usar WSL (recomendado)
wsl --install

# Dentro do WSL:
sudo apt update
sudo apt install redis-server
sudo service redis-server start

# Opção 2: Usar Docker Desktop
docker run -d -p 6379:6379 redis:latest
```

### Verificação
```powershell
redis-cli ping
# Output esperado: PONG
```

---

## PASSO 1.5: Instalar VS Code

```powershell
# Baixar de code.visualstudio.com
# Ou usar winget
winget install Microsoft.VisualStudioCode

# Extensões recomendadas:
# - Python (Microsoft)
# - Pylance
# - Django (Baptiste Darthenay)
# - ES7+ React/Redux/React-Native snippets
# - Tailwind CSS IntelliSense
# - ESLint
# - Prettier
```

---

## PASSO 1.6: Criar Estrutura de Pastas

```powershell
# Criar pasta principal
cd D:\Projectos
mkdir bet-insight
cd bet-insight

# Criar estrutura
mkdir backend
mkdir frontend
mkdir docs
mkdir docker

# Inicializar Git
git init
git branch -M main
```

---

## PASSO 1.7: Criar .gitignore Global

```powershell
# Criar arquivo .gitignore na raiz
New-Item .gitignore
```

```gitignore
# .gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv
*.egg-info/
dist/
build/

# Django
*.log
db.sqlite3
media/
staticfiles/

# Environment
.env
.env.local

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# React
build/
.DS_Store
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
Thumbs.db
.DS_Store
```

---

# 📋 FASE 2: BACKEND DJANGO - FUNDAÇÃO

## Objetivo
Criar e configurar o projeto Django básico com autenticação.

---

## PASSO 2.1: Criar Ambiente Virtual Python

```powershell
cd D:\Projectos\bet-insight\backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\activate

# Você verá (venv) no início do prompt
```

---

## PASSO 2.2: Instalar Django e Dependências

```powershell
# Com venv ativado

# Criar arquivo requirements.txt
New-Item requirements.txt
```

```txt
# requirements.txt

Django==5.0.1
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
psycopg2-binary==2.9.9
python-decouple==3.8
Pillow==10.2.0
requests==2.31.0
```

```powershell
# Instalar tudo
pip install -r requirements.txt
```

### Verificação
```powershell
pip list
# Deve mostrar todas as bibliotecas instaladas
```

---

## PASSO 2.3: Criar Projeto Django

```powershell
# Criar projeto Django
django-admin startproject config .

# Estrutura criada:
# backend/
# ├── config/
# │   ├── __init__.py
# │   ├── settings.py
# │   ├── urls.py
# │   ├── wsgi.py
# │   └── asgi.py
# └── manage.py
```

---

## PASSO 2.4: Criar Apps Django

```powershell
# Criar apps
python manage.py startapp users
python manage.py startapp matches
python manage.py startapp analysis
python manage.py startapp subscriptions

# Organizar em pasta apps
mkdir apps
Move-Item users apps\
Move-Item matches apps\
Move-Item analysis apps\
Move-Item subscriptions apps\
```

---

## PASSO 2.5: Configurar settings.py

```python
# config/settings.py

from pathlib import Path
from decouple import config
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-temporary-key-change-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Applications
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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='betinsight_db'),
        'USER': config('DB_USER', default='betinsight_user'),
        'PASSWORD': config('DB_PASSWORD', default='senha_forte_aqui'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

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
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

CORS_ALLOW_CREDENTIALS = True

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

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

---

## PASSO 2.6: Criar arquivo .env

```powershell
# Criar .env na pasta backend
New-Item .env
```

```env
# .env

# Django
SECRET_KEY=django-insecure-sua-chave-secreta-aqui-mude-em-producao
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=betinsight_db
DB_USER=betinsight_user
DB_PASSWORD=senha_forte_aqui
DB_HOST=localhost
DB_PORT=5432

# APIs (preencher depois)
GEMINI_API_KEY=
FOOTBALL_API_KEY=
MPESA_API_KEY=
```

---

## PASSO 2.7: Criar Modelo User Customizado

```python
# apps/users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Modelo customizado de usuário para Bet Insight"""
    
    # Sobrescrever email para ser único
    email = models.EmailField(_('email'), unique=True)
    
    # Informações adicionais
    phone = models.CharField(
        _('telefone'),
        max_length=20,
        unique=True,
        help_text='Formato: +258XXXXXXXXX'
    )
    
    # Sistema de créditos
    daily_analysis_count = models.IntegerField(
        _('análises usadas hoje'),
        default=0,
        help_text='Resetado diariamente à meia-noite'
    )
    daily_analysis_limit = models.IntegerField(
        _('limite diário de análises'),
        default=5,
        help_text='5 para grátis, ilimitado para premium'
    )
    
    # Status Premium
    is_premium = models.BooleanField(
        _('é usuário premium'),
        default=False
    )
    premium_until = models.DateTimeField(
        _('premium válido até'),
        null=True,
        blank=True
    )
    
    # Push Notifications
    fcm_token = models.CharField(
        _('token FCM'),
        max_length=255,
        blank=True,
        help_text='Token para push notifications (Firebase)'
    )
    notifications_enabled = models.BooleanField(
        _('notificações ativadas'),
        default=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    
    # Configurações de autenticação
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']
    
    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    def can_analyze(self):
        """Verifica se usuário pode fazer mais análises hoje"""
        if self.is_premium:
            return True
        return self.daily_analysis_count < self.daily_analysis_limit
    
    def increment_analysis_count(self):
        """Incrementa contador de análises"""
        if not self.is_premium:
            self.daily_analysis_count += 1
            self.save(update_fields=['daily_analysis_count'])
    
    def reset_daily_analysis_count(self):
        """Reseta contador (chamado por task diária)"""
        self.daily_analysis_count = 0
        self.save(update_fields=['daily_analysis_count'])
```

---

## PASSO 2.8: Configurar Admin do User

```python
# apps/users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin customizado para modelo User"""
    
    list_display = [
        'email',
        'username',
        'phone',
        'is_premium',
        'daily_analysis_count',
        'created_at'
    ]
    
    list_filter = [
        'is_premium',
        'is_staff',
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'email',
        'username',
        'phone'
    ]
    
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Informações Adicionais'), {
            'fields': (
                'phone',
                'is_premium',
                'premium_until',
                'daily_analysis_count',
                'daily_analysis_limit',
                'fcm_token',
                'notifications_enabled'
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'phone',
                'password1',
                'password2'
            ),
        }),
    )
```

---

## PASSO 2.9: Atualizar apps/__init__.py

```python
# apps/users/__init__.py
default_app_config = 'apps.users.apps.UsersConfig'

# apps/matches/__init__.py
default_app_config = 'apps.matches.apps.MatchesConfig'

# apps/analysis/__init__.py
default_app_config = 'apps.analysis.apps.AnalysisConfig'

# apps/subscriptions/__init__.py
default_app_config = 'apps.subscriptions.apps.SubscriptionsConfig'
```

---

## PASSO 2.10: Fazer Primeira Migration

```powershell
# Criar migrations
python manage.py makemigrations

# Aplicar migrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser
# Email: admin@betinsight.co.mz
# Username: admin
# Phone: +258840000000
# Password: (senha forte)
```

### Verificação
```powershell
# Rodar servidor
python manage.py runserver

# Acessar admin
# http://127.0.0.1:8000/admin/
# Login com credenciais do superusuário
```

**✅ CHECKPOINT FASE 2: Backend básico funcionando com autenticação!**

---

# 📋 FASE 3: BACKEND - MODELS E DATABASE

## Objetivo
Criar todos os modelos de dados necessários.

---

## PASSO 3.1: Criar Models de Matches

```python
# apps/matches/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class League(models.Model):
    """Modelo de Liga/Competição"""
    
    name = models.CharField(_('nome'), max_length=100)
    country = models.CharField(_('país'), max_length=50)
    api_id = models.IntegerField(
        _('ID da API'),
        unique=True,
        help_text='ID da liga na API de futebol'
    )
    logo = models.URLField(_('logo URL'), blank=True)
    is_active = models.BooleanField(_('ativa'), default=True)
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('liga')
        verbose_name_plural = _('ligas')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.country})"


class Team(models.Model):
    """Modelo de Time/Equipe"""
    
    name = models.CharField(_('nome'), max_length=100)
    api_id = models.IntegerField(
        _('ID da API'),
        unique=True
    )
    logo = models.URLField(_('logo URL'), blank=True)
    
    # Estatísticas (cache)
    stats_cache = models.JSONField(
        _('cache de estatísticas'),
        null=True,
        blank=True,
        help_text='Cache temporário de stats da temporada'
    )
    stats_updated_at = models.DateTimeField(
        _('stats atualizadas em'),
        null=True,
        blank=True
    )
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('time')
        verbose_name_plural = _('times')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Match(models.Model):
    """Modelo de Jogo/Partida"""
    
    STATUS_CHOICES = [
        ('scheduled', _('Agendado')),
        ('live', _('Ao Vivo')),
        ('finished', _('Finalizado')),
        ('postponed', _('Adiado')),
        ('cancelled', _('Cancelado')),
    ]
    
    # Identificação
    api_id = models.IntegerField(
        _('ID da API'),
        unique=True
    )
    
    # Relacionamentos
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
    
    # Data e Status
    match_date = models.DateTimeField(_('data e hora do jogo'))
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    
    # Resultado
    home_score = models.IntegerField(
        _('gols casa'),
        null=True,
        blank=True
    )
    away_score = models.IntegerField(
        _('gols fora'),
        null=True,
        blank=True
    )
    
    # Informações adicionais
    venue = models.CharField(_('estádio'), max_length=100, blank=True)
    referee = models.CharField(_('árbitro'), max_length=100, blank=True)
    round = models.CharField(_('rodada'), max_length=50, blank=True)
    season = models.CharField(_('temporada'), max_length=20, default='2024/2025')
    
    # Cache de dados para análise
    stats_cache = models.JSONField(
        _('cache de estatísticas'),
        null=True,
        blank=True,
        help_text='Dados completos para análise (forma, H2H, stats)'
    )
    stats_updated_at = models.DateTimeField(
        _('stats atualizadas em'),
        null=True,
        blank=True
    )
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('jogo')
        verbose_name_plural = _('jogos')
        ordering = ['match_date']
        indexes = [
            models.Index(fields=['match_date', 'status']),
            models.Index(fields=['league', 'match_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.match_date.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def result(self):
        """Retorna resultado do jogo (1, X ou 2)"""
        if self.status != 'finished' or self.home_score is None:
            return None
        
        if self.home_score > self.away_score:
            return '1'
        elif self.home_score < self.away_score:
            return '2'
        else:
            return 'X'
```

---

## PASSO 3.2: Criar Models de Analysis

```python
# apps/analysis/models.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Analysis(models.Model):
    """Modelo de Análise com IA"""
    
    CONFIDENCE_CHOICES = [
        (1, '1 estrela - Baixa'),
        (2, '2 estrelas - Média-Baixa'),
        (3, '3 estrelas - Média'),
        (4, '4 estrelas - Alta'),
        (5, '5 estrelas - Muito Alta'),
    ]
    
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
    
    # Previsão (Probabilidades)
    home_probability = models.DecimalField(
        _('probabilidade casa (%)'),
        max_digits=5,
        decimal_places=2,
        help_text='Probabilidade de vitória do time casa'
    )
    draw_probability = models.DecimalField(
        _('probabilidade empate (%)'),
        max_digits=5,
        decimal_places=2
    )
    away_probability = models.DecimalField(
        _('probabilidade fora (%)'),
        max_digits=5,
        decimal_places=2,
        help_text='Probabilidade de vitória do time visitante'
    )
    
    # Recomendações
    recommendation = models.CharField(
        _('recomendação principal'),
        max_length=255,
        help_text='Ex: Apostar em Liverpool Vence (2)'
    )
    alternative_recommendation = models.CharField(
        _('recomendação alternativa'),
        max_length=255,
        blank=True,
        help_text='Ex: Over 2.5 gols'
    )
    
    # Confiança
    confidence = models.IntegerField(
        _('nível de confiança'),
        choices=CONFIDENCE_CHOICES,
        help_text='De 1 (baixa) a 5 (muito alta)'
    )
    
    # Análise Detalhada
    reasoning = models.TextField(
        _('raciocínio da análise'),
        help_text='Explicação detalhada da previsão'
    )
    key_factors = models.JSONField(
        _('fatores-chave'),
        help_text='Lista de fatores que apoiam a previsão'
    )
    risk_factors = models.JSONField(
        _('fatores de risco'),
        help_text='Lista de riscos ou incertezas'
    )
    expected_goals = models.JSONField(
        _('gols esperados'),
        help_text='xG: {home: 1.2, away: 2.1, total: 3.3}'
    )
    
    # Apostas Detalhadas
    detailed_bets = models.JSONField(
        _('apostas detalhadas'),
        null=True,
        blank=True,
        help_text='Array de apostas com mercados diferentes'
    )
    
    # Dados Brutos da Análise
    analysis_data = models.JSONField(
        _('dados completos da análise'),
        help_text='Todos os dados usados na análise'
    )
    
    # Validação (após jogo)
    is_validated = models.BooleanField(
        _('foi validado'),
        default=False,
        help_text='True após jogo finalizado'
    )
    was_correct = models.BooleanField(
        _('previsão estava correta'),
        null=True,
        blank=True
    )
    actual_result = models.CharField(
        _('resultado real'),
        max_length=1,
        blank=True,
        choices=[
            ('1', 'Casa venceu'),
            ('X', 'Empate'),
            ('2', 'Fora venceu')
        ]
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('análise')
        verbose_name_plural = _('análises')
        ordering = ['-created_at']
        unique_together = ['user', 'match']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['match', '-created_at']),
            models.Index(fields=['is_validated', 'was_correct']),
        ]
    
    def __str__(self):
        return f"Análise de {self.user.username} - {self.match}"
    
    def validate_prediction(self):
        """
        Valida previsão após jogo finalizado.
        Compara previsão com resultado real.
        """
        if self.match.status != 'finished' or self.match.result is None:
            return
        
        # Determinar previsão feita
        probabilities = [
            ('1', float(self.home_probability)),
            ('X', float(self.draw_probability)),
            ('2', float(self.away_probability))
        ]
        predicted = max(probabilities, key=lambda x: x[1])[0]
        
        # Comparar com resultado real
        self.actual_result = self.match.result
        self.was_correct = (predicted == self.match.result)
        self.is_validated = True
        self.save(update_fields=['actual_result', 'was_correct', 'is_validated'])
```

---

## PASSO 3.3: Criar Models de Subscriptions

```python
# apps/subscriptions/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta

class Subscription(models.Model):
    """Modelo de Assinatura Premium"""
    
    STATUS_CHOICES = [
        ('pending', _('Pendente')),
        ('active', _('Ativo')),
        ('expired', _('Expirado')),
        ('cancelled', _('Cancelado')),
    ]
    
    # Relacionamento
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name=_('usuário')
    )
    
    # Período
    start_date = models.DateTimeField(_('data de início'))
    end_date = models.DateTimeField(_('data de término'))
    
    # Status
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Valores
    amount = models.DecimalField(
        _('valor pago'),
        max_digits=10,
        decimal_places=2,
        help_text='Valor em MZN'
    )
    currency = models.CharField(
        _('moeda'),
        max_length=3,
        default='MZN'
    )
    
    # Pagamento
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
        _('comprovante de pagamento'),
        upload_to='payment_proofs/%Y/%m/',
        null=True,
        blank=True
    )
    
    # Auto-renovação
    auto_renew = models.BooleanField(
        _('renovação automática'),
        default=False
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('assinatura')
        verbose_name_plural = _('assinaturas')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Assinatura de {self.user.email} - {self.get_status_display()}"
    
    def is_active(self):
        """Verifica se assinatura está ativa no momento"""
        return (
            self.status == 'active' and
            self.end_date > timezone.now()
        )
    
    def activate(self):
        """Ativa a assinatura"""
        self.status = 'active'
        self.user.is_premium = True
        self.user.premium_until = self.end_date
        self.user.save(update_fields=['is_premium', 'premium_until'])
        self.save(update_fields=['status'])
    
    def expire(self):
        """Expira a assinatura"""
        self.status = 'expired'
        self.user.is_premium = False
        self.user.premium_until = None
        self.user.save(update_fields=['is_premium', 'premium_until'])
        self.save(update_fields=['status'])
    
    def cancel(self):
        """Cancela a assinatura"""
        self.status = 'cancelled'
        self.user.is_premium = False
        self.user.premium_until = None
        self.user.save(update_fields=['is_premium', 'premium_until'])
        self.save(update_fields=['status'])
    
    @staticmethod
    def create_monthly_subscription(user, amount=499):
        """
        Cria nova assinatura mensal para usuário
        """
        start_date = timezone.now()
        end_date = start_date + timedelta(days=30)
        
        subscription = Subscription.objects.create(
            user=user,
            start_date=start_date,
            end_date=end_date,
            amount=amount,
            currency='MZN',
            payment_method='mpesa'
        )
        
        return subscription


class Payment(models.Model):
    """Modelo de Pagamento individual"""
    
    STATUS_CHOICES = [
        ('pending', _('Pendente')),
        ('processing', _('Processando')),
        ('completed', _('Completo')),
        ('failed', _('Falhou')),
        ('refunded', _('Reembolsado')),
    ]
    
    # Relacionamento
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('assinatura')
    )
    
    # Valores
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
    
    # M-Pesa
    mpesa_transaction_id = models.CharField(
        _('ID transação M-Pesa'),
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )
    mpesa_phone = models.CharField(
        _('telefone M-Pesa'),
        max_length=20,
        help_text='+258XXXXXXXXX'
    )
    mpesa_response = models.JSONField(
        _('resposta M-Pesa'),
        null=True,
        blank=True,
        help_text='Resposta completa da API M-Pesa'
    )
    
    # Status
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    completed_at = models.DateTimeField(
        _('completado em'),
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _('pagamento')
        verbose_name_plural = _('pagamentos')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pagamento {self.mpesa_transaction_id} - {self.get_status_display()}"
    
    def mark_as_completed(self):
        """Marca pagamento como completo e ativa assinatura"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
        
        # Ativar assinatura
        self.subscription.activate()
    
    def mark_as_failed(self):
        """Marca pagamento como falho"""
        self.status = 'failed'
        self.save(update_fields=['status'])
```

---

## PASSO 3.4: Configurar Admin dos Models

```python
# apps/matches/admin.py

from django.contrib import admin
from .models import League, Team, Match

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'is_active', 'created_at']
    list_filter = ['is_active', 'country']
    search_fields = ['name', 'country']
    ordering = ['name']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'api_id', 'created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'home_team',
        'away_team',
        'league',
        'match_date',
        'status',
        'score'
    ]
    list_filter = ['status', 'league', 'match_date']
    search_fields = ['home_team__name', 'away_team__name']
    date_hierarchy = 'match_date'
    ordering = ['-match_date']
    
    def score(self, obj):
        if obj.home_score is not None and obj.away_score is not None:
            return f"{obj.home_score} - {obj.away_score}"
        return "-"
    score.short_description = 'Placar'
```

```python
# apps/analysis/admin.py

from django.contrib import admin
from .models import Analysis

@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'match',
        'recommendation',
        'confidence',
        'was_correct',
        'created_at'
    ]
    list_filter = [
        'confidence',
        'is_validated',
        'was_correct',
        'created_at'
    ]
    search_fields = [
        'user__email',
        'match__home_team__name',
        'match__away_team__name'
    ]
    readonly_fields = [
        'created_at',
        'is_validated',
        'was_correct',
        'actual_result'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
```

```python
# apps/subscriptions/admin.py

from django.contrib import admin
from .models import Subscription, Payment

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'status',
        'start_date',
        'end_date',
        'amount',
        'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'payment_reference']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    actions = ['activate_subscriptions', 'expire_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        for subscription in queryset:
            subscription.activate()
        self.message_user(request, f"{queryset.count()} assinaturas ativadas")
    activate_subscriptions.short_description = "Ativar assinaturas selecionadas"
    
    def expire_subscriptions(self, request, queryset):
        for subscription in queryset:
            subscription.expire()
        self.message_user(request, f"{queryset.count()} assinaturas expiradas")
    expire_subscriptions.short_description = "Expirar assinaturas selecionadas"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'subscription',
        'mpesa_transaction_id',
        'amount',
        'status',
        'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = [
        'mpesa_transaction_id',
        'mpesa_phone',
        'subscription__user__email'
    ]
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
```

---

## PASSO 3.5: Criar e Aplicar Migrations

```powershell
# Criar migrations
python manage.py makemigrations users
python manage.py makemigrations matches
python manage.py makemigrations analysis
python manage.py makemigrations subscriptions

# Aplicar migrations
python manage.py migrate

# Verificar no admin
python manage.py runserver
# Acesse http://127.0.0.1:8000/admin/
```

### Verificação
- [ ] Modelo User aparece no admin
- [ ] Modelos de Matches aparecem no admin
- [ ] Modelos de Analysis aparecem no admin
- [ ] Modelos de Subscriptions aparecem no admin

**✅ CHECKPOINT FASE 3: Todos os models criados e funcionando!**

---

*Continua na próxima mensagem com FASE 4: API Endpoints...*

Quer que eu continue com as próximas fases? Ainda falta:
- Fase 4-6: APIs Backend
- Fase 7-12: Frontend React completo
- Fase 13-15: Testes e Deploy
