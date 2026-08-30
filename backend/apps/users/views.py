from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema_view, extend_schema

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer



@extend_schema_view(
    post=extend_schema(tags=['Users'], summary='Зарегистрироваться'),
)
class RegisterView(generics.CreateAPIView):
    """POST /api/v1/auth/register/"""
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )

@extend_schema_view(
    post=extend_schema(tags=['Users'], summary='Войти в систему'),
)
class LoginView(APIView):
    """POST /api/v1/auth/login/"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=LoginSerializer,
        responses={200: UserSerializer},
        summary='Вход по email и паролю',
        description='Возвращает access и refresh токены при успешной авторизации.',
    )

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })

@extend_schema_view(
    post=extend_schema(tags=['Users'], summary='Выйти из системы'),
)
class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/
    Добавляет refresh token в blacklist — после этого его нельзя
    использовать для получения нового access token.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request={'application/json': {'type': 'object', 'properties': {'refresh': {'type': 'string'}}}},
        responses={205: None, 400: dict},
        summary='Выход из системы',
        description='Добавляет refresh token в blacklist.',
    )

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
        except (KeyError, TokenError):
            return Response(
                {'detail': 'Невалидный или отсутствующий refresh token'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_205_RESET_CONTENT)

@extend_schema_view(
    get=extend_schema(tags=['Users'], summary='Мой профиль'),
    patch=extend_schema(tags=['Users'], summary='Обновить профиль'),
)
class MeView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/v1/auth/me/  — получить профиль
    PATCH /api/v1/auth/me/  — обновить профиль
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user