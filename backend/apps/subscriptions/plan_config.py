"""
Configuração de Planos de Assinatura
PlacarCerto Mozambique
"""

PLANS = {
    'freemium': {
        'name': 'Freemium',
        'slug': 'freemium',
        'price': 0,
        'daily_analysis_limit': 3,
        'duration_days': None,  # Permanente
        'features': [
            '3 análises por dia',
            'Análise de IA básica',
            'Histórico de 7 dias',
            'Acesso a ligas principais',
        ],
        'description': 'Teste grátis antes de assinar',
        'is_active': True,
        'color': 'gray',
    },
    'teste': {
        'name': 'Teste (1 MZN)',
        'slug': 'teste',
        'price': 1,
        'daily_analysis_limit': 3,
        'duration_days': 1,  # 1 dia apenas
        'features': [
            '3 análises por dia',
            'Análise de IA básica',
            'Válido por 1 dia',
            '🧪 Apenas para testes de pagamento',
        ],
        'description': 'Plano de teste - 1 MZN',
        'is_active': True,
        'color': 'green',
        'popular': False,
    },
    'starter': {
        'name': 'Starter',
        'slug': 'starter',
        'price': 299,
        'daily_analysis_limit': 15,
        'duration_days': 30,
        'trial_days': 7,
        'features': [
            '15 análises por dia',
            'Análise de IA avançada',
            'Histórico 30 dias',
            'Todas as ligas',
            '🎁 7 dias grátis',
        ],
        'description': 'Ideal para apostadores casuais',
        'is_active': True,
        'color': 'blue',
        'popular': False,
    },
    'pro': {
        'name': 'Pro',
        'slug': 'pro',
        'price': 599,
        'daily_analysis_limit': 40,
        'duration_days': 30,
        'features': [
            '40 análises por dia',
            'Análise de IA avançada',
            'Histórico ilimitado',
            'Todas as ligas',
            'Suporte prioritário',
            'Notificações em tempo real',
        ],
        'description': 'Perfeito para apostadores regulares',
        'is_active': True,
        'color': 'primary',
        'popular': True,
    },
    'vip': {
        'name': 'VIP',
        'slug': 'vip',
        'price': 1499,
        'daily_analysis_limit': 80,
        'duration_days': 90,
        'features': [
            '80 análises por dia',
            'Análise de IA avançada',
            'Histórico ilimitado',
            'Todas as ligas',
            'Suporte WhatsApp dedicado',
            'Análises prioritárias',
            'Estatísticas avançadas',
            '💰 Economize 298 MZN',
        ],
        'description': 'Melhor custo-benefício',
        'is_active': True,
        'color': 'yellow',
        'popular': False,
        'savings': 298,  # Economia em MZN vs 3x pro
    },
}


def get_plan(slug):
    """Retorna configuração de um plano pelo slug"""
    return PLANS.get(slug)


def get_active_plans():
    """Retorna apenas planos ativos"""
    return {k: v for k, v in PLANS.items() if v.get('is_active', True)}


def get_premium_plans():
    """Retorna apenas planos pagos (excluindo freemium)"""
    return {k: v for k, v in PLANS.items() if v['price'] > 0 and v.get('is_active', True)}


def get_plan_limit(slug):
    """Retorna o limite diário de análises de um plano"""
    plan = get_plan(slug)
    return plan['daily_analysis_limit'] if plan else 5  # Default freemium


def get_plan_price(slug):
    """Retorna o preço de um plano"""
    plan = get_plan(slug)
    return plan['price'] if plan else 0


def get_plan_duration(slug):
    """Retorna a duração em dias de um plano"""
    plan = get_plan(slug)
    return plan['duration_days'] if plan else None
