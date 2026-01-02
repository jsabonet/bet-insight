from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.throttling import ScopedRateThrottle
from .plan_config import get_active_plans, get_premium_plans, get_plan
from .serializers import PlanSerializer, SubscriptionSerializer
from .models import Subscription
from django.utils import timezone
from django.db import transaction
from datetime import timedelta


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_assign_subscription(request):
    """
    Admin: atribui uma assinatura premium a um usuário.

    Body:
    {
      "user_id": 123,
      "plan_slug": "starter|pro|vip",
      "duration_days": optional override
    }
    """
    from apps.users.models import User
    user_id = request.data.get('user_id')
    plan_slug = request.data.get('plan_slug')
    duration_override = request.data.get('duration_days')

    if not user_id or not plan_slug:
        return Response({
            'error': 'Parâmetros obrigatórios: user_id, plan_slug'
        }, status=status.HTTP_400_BAD_REQUEST)

    plan = get_plan(plan_slug)
    if not plan:
        return Response({
            'error': 'Plano inválido'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

    # Se o destino for freemium, apenas cancelar e retornar stub
    if plan_slug == 'freemium':
        with transaction.atomic():
            current = user.subscriptions.filter(status='active', end_date__gt=timezone.now()).first()
            if current:
                current.cancel()
        # Retornar um stub compatível com frontend
        free = get_plan('freemium')
        return Response({
            'message': 'Assinatura removida; usuário agora em freemium',
            'subscription': {
                'plan': 'freemium',
                'plan_slug': 'freemium',
                'status': 'active',
                'is_active': True,
                'daily_limit': free['daily_analysis_limit'],
                'plan_details': {
                    'name': free['name'],
                    'price': free['price'],
                    'features': free['features'],
                    'color': free.get('color', 'gray'),
                    'description': free.get('description', ''),
                }
            }
        })

    # Para planos pagos, criar assinatura com end_date explícita
    with transaction.atomic():
        current = user.subscriptions.filter(status='active', end_date__gt=timezone.now()).first()
        if current:
            current.cancel()

        start = timezone.now()
        # Determinar duração
        if duration_override and isinstance(duration_override, int) and duration_override > 0:
            duration_days = duration_override
        else:
            duration_days = plan.get('duration_days')

        if not isinstance(duration_days, int) or duration_days <= 0:
            return Response({'error': 'Plano sem duração válida'}, status=status.HTTP_400_BAD_REQUEST)

        end = start + timedelta(days=duration_days)

        sub = Subscription.objects.create(
            user=user,
            plan=plan_slug,
            plan_slug=plan_slug,
            status='active',
            start_date=start,
            end_date=end,
            auto_renew=False,
            amount_paid=plan['price']
        )

    return Response({
        'message': 'Assinatura atribuída com sucesso',
        'subscription': SubscriptionSerializer(sub).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_remove_subscription(request):
    """
    Admin: remove (cancela) a assinatura premium ativa de um usuário.

    Body:
    {
      "user_id": 123
    }
    """
    from apps.users.models import User
    user_id = request.data.get('user_id')

    if not user_id:
        return Response({'error': 'Parâmetro obrigatório: user_id'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

    current = user.subscriptions.filter(status='active', end_date__gt=timezone.now()).first()
    if not current:
        return Response({'message': 'Usuário não possui assinatura ativa'}, status=status.HTTP_200_OK)

    current.cancel()

    return Response({
        'message': 'Assinatura removida com sucesso',
        'subscription': SubscriptionSerializer(current).data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
def list_plans(request):
    """
    Lista todos os planos disponíveis
    Endpoint público para exibir opções de planos
    """
    plans_dict = get_active_plans()
    
    # Converter dict para lista de objetos serializáveis
    plans_list = []
    for slug, plan_data in plans_dict.items():
        plan_obj = {
            'slug': slug,
            **plan_data
        }
        plans_list.append(plan_obj)
    
    # Ordenar: freemium primeiro, depois por preço
    plans_list.sort(key=lambda x: (x['price'] if x['price'] > 0 else -1))
    
    # Retornar diretamente os planos para evitar erros de serialização
    # Aplicar throttle por escopo
    list_plans.throttle_classes = [ScopedRateThrottle]
    list_plans.throttle_scope = 'plans'
    return Response(plans_list)
list_plans.throttle_scope = 'plans'


@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
def list_premium_plans(request):
    """
    Lista apenas planos premium (pagos)
    Para tela de upgrade/assinatura
    """
    plans_dict = get_premium_plans()
    
    plans_list = []
    for slug, plan_data in plans_dict.items():
        plan_obj = {
            'slug': slug,
            **plan_data
        }
        plans_list.append(plan_obj)
    
    # Ordenar por preço
    plans_list.sort(key=lambda x: x['price'])
    
    serializer = PlanSerializer(plans_list, many=True)
    return Response(serializer.data)
list_premium_plans.throttle_scope = 'plans'


@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
def get_plan_details(request, slug):
    """
    Retorna detalhes de um plano específico
    """
    plan = get_plan(slug)
    
    if not plan:
        return Response(
            {'error': 'Plano não encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    plan_obj = {'slug': slug, **plan}
    return Response(plan_obj)
get_plan_details.throttle_scope = 'plans'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_subscription(request):
    """
    Retorna assinatura ativa do usuário atual
    """
    from django.utils import timezone
    
    subscription = request.user.subscriptions.filter(
        status='active',
        end_date__gt=timezone.now()
    ).first()
    
    if not subscription:
        # Usuário sem assinatura = freemium
        return Response({
            'plan': 'freemium',
            'plan_slug': 'freemium',
            'status': 'active',
            'daily_limit': get_plan('freemium')['daily_analysis_limit'],
            'is_active': True,
            'plan_details': {
                'name': 'Freemium',
                'price': 0,
                'features': get_plan('freemium')['features'],
                'color': 'gray',
            }
        })
    
    serializer = SubscriptionSerializer(subscription)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    """
    Cancela assinatura ativa do usuário
    """
    from django.utils import timezone
    
    subscription = request.user.subscriptions.filter(
        status='active',
        end_date__gt=timezone.now()
    ).first()
    
    if not subscription:
        return Response(
            {'error': 'Nenhuma assinatura ativa encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if subscription.plan_slug == 'freemium':
        return Response(
            {'error': 'Não é possível cancelar plano gratuito'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    subscription.cancel()
    
    return Response({
        'message': 'Assinatura cancelada com sucesso',
        'subscription': SubscriptionSerializer(subscription).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_history(request):
    """
    Histórico de assinaturas do usuário
    """
    subscriptions = request.user.subscriptions.all().order_by('-created_at')
    serializer = SubscriptionSerializer(subscriptions, many=True)
    return Response(serializer.data)
