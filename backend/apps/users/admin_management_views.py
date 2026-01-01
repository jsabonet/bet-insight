"""
Views de gerenciamento avançado de usuários para Admin
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from .models import User
from .serializers import UserSerializer


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_toggle_admin_status(request, user_id):
    """
    Admin: Tornar usuário admin ou remover privilégios de admin
    
    Body:
    {
        "is_staff": true/false,
        "is_superuser": false  (opcional, apenas superusers podem criar outros superusers)
    }
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'Usuário não encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Verificar se está tentando modificar a si mesmo
    if user.id == request.user.id:
        return Response(
            {'error': 'Você não pode modificar seus próprios privilégios de admin'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    is_staff = request.data.get('is_staff')
    is_superuser = request.data.get('is_superuser', False)
    
    if is_staff is None:
        return Response(
            {'error': 'Parâmetro obrigatório: is_staff (true/false)'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Apenas superusers podem criar outros superusers
    if is_superuser and not request.user.is_superuser:
        return Response(
            {'error': 'Apenas superusuários podem criar outros superusuários'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Atualizar status
    user.is_staff = is_staff
    if request.user.is_superuser:
        user.is_superuser = is_superuser
    user.save()
    
    action = 'promovido a admin' if is_staff else 'removido de admin'
    if is_superuser:
        action = 'promovido a superusuário'
    
    return Response({
        'message': f'Usuário {user.username} {action} com sucesso',
        'user': UserSerializer(user).data
    })


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def admin_update_user(request, user_id):
    """
    Admin: Editar informações de qualquer usuário
    
    Body pode conter qualquer campo editável:
    {
        "username": "novo_username",
        "email": "novo@email.com",
        "phone": "841234567",
        "is_premium": true,
        "premium_until": "2026-12-31T23:59:59Z",
        "daily_analysis_count": 0,
        "is_active": true
    }
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'Usuário não encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Campos que podem ser editados
    editable_fields = [
        'username', 'email', 'phone', 'first_name', 'last_name',
        'is_premium', 'premium_until', 'daily_analysis_count',
        'is_active', 'push_enabled'
    ]
    
    # Campos sensíveis (apenas superuser pode editar)
    sensitive_fields = ['is_staff', 'is_superuser']
    
    # Validar e aplicar mudanças
    updated_fields = []
    
    # Processar premium_until com timezone
    if 'premium_until' in request.data and request.data['premium_until']:
        try:
            # Converter string ISO para datetime com timezone
            premium_date = datetime.fromisoformat(request.data['premium_until'].replace('Z', '+00:00'))
            # Garantir que tem timezone
            if premium_date.tzinfo is None:
                premium_date = timezone.make_aware(premium_date)
            user.premium_until = premium_date
            updated_fields.append('premium_until')
        except (ValueError, AttributeError) as e:
            return Response(
                {'error': f'Data inválida para premium_until: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    elif 'premium_until' in request.data and not request.data['premium_until']:
        # Se veio vazio, setar como None
        user.premium_until = None
        updated_fields.append('premium_until')
    
    # Aplicar outros campos
    for field in editable_fields:
        if field in request.data and field != 'premium_until':  # Já tratamos premium_until
            setattr(user, field, request.data[field])
            updated_fields.append(field)
    
    # Superuser pode editar campos sensíveis
    if request.user.is_superuser:
        for field in sensitive_fields:
            if field in request.data:
                # Não permitir remover is_superuser de si mesmo
                if field == 'is_superuser' and user.id == request.user.id:
                    continue
                setattr(user, field, request.data[field])
                updated_fields.append(field)
    
    # Validar username único
    if 'username' in updated_fields:
        if User.objects.filter(username=user.username).exclude(id=user.id).exists():
            return Response(
                {'error': 'Username já está em uso'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Validar email único
    if 'email' in updated_fields:
        if User.objects.filter(email=user.email).exclude(id=user.id).exists():
            return Response(
                {'error': 'Email já está em uso'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    try:
        user.save()
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Erro ao salvar usuário: {error_detail}")
        return Response(
            {'error': f'Erro ao salvar usuário: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response({
        'message': f'Usuário {user.username} atualizado com sucesso',
        'updated_fields': updated_fields,
        'user': UserSerializer(user).data
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_reset_user_password(request, user_id):
    """
    Admin: Resetar senha de usuário
    
    Body:
    {
        "new_password": "nova_senha_123"
    }
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'Usuário não encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    new_password = request.data.get('new_password')
    
    if not new_password:
        return Response(
            {'error': 'Parâmetro obrigatório: new_password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(new_password) < 6:
        return Response(
            {'error': 'A senha deve ter no mínimo 6 caracteres'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Não permitir resetar senha de superusuário (exceto por outro superusuário)
    if user.is_superuser and not request.user.is_superuser:
        return Response(
            {'error': 'Apenas superusuários podem resetar senha de outros superusuários'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    user.set_password(new_password)
    user.save()
    
    return Response({
        'message': f'Senha do usuário {user.username} resetada com sucesso',
        'user_id': user.id,
        'username': user.username
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_list_all_users(request):
    """
    Admin: Listar todos os usuários com filtros avançados
    
    Query params:
    - search: busca por username, email ou phone
    - is_premium: true/false
    - is_staff: true/false
    - is_active: true/false
    - page: número da página
    - page_size: tamanho da página (padrão 20)
    """
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    users = User.objects.all().order_by('-created_at')
    
    # Filtros
    search = request.query_params.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    is_premium = request.query_params.get('is_premium')
    if is_premium is not None:
        users = users.filter(is_premium=is_premium.lower() == 'true')
    
    is_staff = request.query_params.get('is_staff')
    if is_staff is not None:
        users = users.filter(is_staff=is_staff.lower() == 'true')
    
    is_active = request.query_params.get('is_active')
    if is_active is not None:
        users = users.filter(is_active=is_active.lower() == 'true')
    
    # Paginação
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    
    paginator = Paginator(users, page_size)
    page_obj = paginator.get_page(page)
    
    return Response({
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page,
        'page_size': page_size,
        'results': UserSerializer(page_obj, many=True).data
    })
