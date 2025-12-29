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
        if self.request.method in ['PUT', 'PATCH']:
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
