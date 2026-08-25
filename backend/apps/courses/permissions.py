from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsTeacherOwnerOrReadOnly(BasePermission):
    """
    Чтение доступно всем (в т.ч. анонимам).
    Изменение — только преподавателю-владельцу курса или admin.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_teacher or request.user.is_admin_role)
        )
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_admin_role:
            return True
        # Course -> obj.teacher; Section -> obj.course.teacher; Lesson -> obj.section.course.teacher
        if hasattr(obj, 'teacher'):
            teacher = obj.teacher
        elif hasattr(obj, 'course'):
            teacher = obj.course.teacher
        elif hasattr(obj, 'section'):
            teacher = obj.section.course.teacher
        else:
            teacher = None
        return teacher == request.user    