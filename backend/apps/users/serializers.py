from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'first_name', 'last_name')

    def validate(self, attrs):
        if 'role' in self.initial_data:
            raise serializers.ValidationError({'role': 'Role cannot be set during registration'})

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
        validated_data['role'] = User.Role.STUDENT
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
class AuthResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    access = serializers.CharField()
    refresh = serializers.CharField()


class AdminUserSerializer(serializers.ModelSerializer):
    """Admin-only serializer for user management."""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'avatar', 'role', 'is_active', 'is_staff', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'email', 'full_name', 'is_staff', 'created_at', 'updated_at')

    def validate(self, attrs):
        forbidden_fields = {'password', 'is_superuser', 'is_staff'}
        unsafe_fields = forbidden_fields.intersection(self.initial_data.keys())
        if unsafe_fields:
            raise serializers.ValidationError({
                field: 'This field cannot be changed through this endpoint.'
                for field in sorted(unsafe_fields)
            })

        request = self.context.get('request')
        if request and self.instance == request.user:
            new_role = attrs.get('role', self.instance.role)
            new_is_active = attrs.get('is_active', self.instance.is_active)
            if new_role != User.Role.ADMIN:
                raise serializers.ValidationError({'role': 'Admins cannot demote their own account.'})
            if new_is_active is False:
                raise serializers.ValidationError({'is_active': 'Admins cannot block their own account.'})

        return attrs
