from rest_framework.permissions import BasePermission


class IsAssignmentTeacherOwner(BasePermission):
    """
    Проверяет, что текущий пользователь — преподаватель курса,
    к которому относится задание (через lesson -> section -> course).
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_role:
            return True
        # obj может быть Assignment или AssignmentSubmission
        assignment = obj if hasattr(obj, 'lesson') else obj.assignment
        return assignment.lesson.section.course.teacher == request.user


class IsSubmissionOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.student == request.user