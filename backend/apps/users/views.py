from rest_framework import filters, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema_view, extend_schema

from .models import User
from .permissions import IsAdmin
from .serializers import (
    AdminUserSerializer,
    AuthResponseSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)



@extend_schema_view(
    post=extend_schema(tags=['Users'], summary='Зарегистрироваться'),
)
class RegisterView(generics.CreateAPIView):
    """POST /api/v1/auth/register/"""
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    throttle_scope = 'auth'

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
    throttle_scope = 'auth'
    
    @extend_schema(
        request=LoginSerializer,
        responses={200: AuthResponseSerializer},
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
    throttle_scope = 'auth'
    
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


class ScopedTokenRefreshView(TokenRefreshView):
    """Token refresh endpoint with its own throttle scope."""

    throttle_scope = 'token_refresh'


@extend_schema_view(
    get=extend_schema(tags=['Admin'], summary='List users'),
)
class AdminUserListView(generics.ListAPIView):
    """GET /api/v1/admin/users/."""

    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AdminUserSerializer
    queryset = User.objects.all().order_by('-created_at')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email', 'role', 'is_active']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get('role')
        is_active = self.request.query_params.get('is_active')
        if role:
            queryset = queryset.filter(role=role)
        if is_active is not None:
            normalized = is_active.lower()
            if normalized in {'true', '1', 'yes'}:
                queryset = queryset.filter(is_active=True)
            elif normalized in {'false', '0', 'no'}:
                queryset = queryset.filter(is_active=False)
        return queryset


@extend_schema_view(
    get=extend_schema(tags=['Admin'], summary='Retrieve user'),
    patch=extend_schema(tags=['Admin'], summary='Update user'),
)
class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/v1/admin/users/{id}/."""

    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AdminUserSerializer
    queryset = User.objects.all()
    lookup_field = 'id'
