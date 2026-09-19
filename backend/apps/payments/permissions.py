from rest_framework.permissions import BasePermission


class IsPaymentOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user
            and request.user.is_authenticated
            and (obj.student_id == request.user.id or request.user.is_admin_role)
        )

