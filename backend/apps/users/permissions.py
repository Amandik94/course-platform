from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_student)


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_teacher)


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin_role)


class IsOwner(BasePermission):
    """
    Проверяет, что объект принадлежит текущему пользователю.
    Ожидает, что у объекта есть поле `owner` или переопределён метод.
    Используется как object-level permission (has_object_permission),
    поэтому в DRF нужно явно вызывать check_object_permissions в view,
    либо использовать generics/ViewSet — они делают это автоматически.
    """
    def has_object_permission(self, request, view, obj):
        owner_field = getattr(view, 'owner_field', 'owner')
        return getattr(obj, owner_field, None) == request.user