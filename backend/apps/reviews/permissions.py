from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsReviewOwnerOrAdminDeleteOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'DELETE' and request.user.is_admin_role:
            return True
        return obj.student_id == request.user.id
