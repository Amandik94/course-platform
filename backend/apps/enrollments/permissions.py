from rest_framework.permissions import BasePermission


class IsEnrollmentOwner(BasePermission):
    """Студент может видеть/управлять только свои записи."""
    def has_object_permission(self, request, view, obj):
        
        return obj.student == request.user