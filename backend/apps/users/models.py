from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя. Email вместо username.

    AbstractBaseUser даёт: password, last_login, is_authenticated и т.д.
    PermissionsMixin даёт: is_superuser, groups, permissions —
    это нужно, чтобы Django admin продолжал нормально работать.
    """

    class Role(models.TextChoices):
        STUDENT = 'student', 'Студент'
        TEACHER = 'teacher', 'Преподаватель'
        ADMIN = 'admin', 'Администратор'

    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    avatar = models.ImageField(
        upload_to='avatars/', null=True, blank=True, verbose_name='Аватар'
    )
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.STUDENT, verbose_name='Роль'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # нужен для доступа в /admin/
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'          # какое поле используется при login()
    REQUIRED_FIELDS = ['first_name', 'last_name']  # спрашивается при createsuperuser

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.email} ({self.get_role_display()})'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN