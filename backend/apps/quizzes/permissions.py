from rest_framework.permissions import BasePermission


class IsQuizTeacherOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_role:
            return True
        quiz = obj if hasattr(obj, 'lesson') else obj.quiz
        return quiz.lesson.section.course.teacher == request.user