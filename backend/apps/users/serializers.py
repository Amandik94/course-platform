from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'first_name', 'last_name', 'role')
        extra_kwargs = {
            'role': {'required': False},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Пароли не совпадают'})

        # Регистрация как admin через публичный endpoint запрещена —
        # админов создаём только через createsuperuser или Django admin
        if attrs.get('role') == User.Role.ADMIN:
            raise serializers.ValidationError({'role': 'Недопустимое значение роли'})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Неверный email или пароль')
        if not user.is_active:
            raise serializers.ValidationError('Аккаунт заблокирован')
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Используется для GET/PATCH /auth/me/"""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'avatar', 'role', 'created_at',
        )
        read_only_fields = ('id', 'email', 'role', 'created_at')
        # email и role нельзя менять через /me/ — email - идентификатор,
        # role меняется только администратором через отдельный endpoint