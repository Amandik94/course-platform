from django.db.models import Q, QuerySet

from .models import Course


def visible_courses_for_user(user) -> QuerySet:
    qs = Course.objects.all()
    if user.is_authenticated:
        if user.is_admin_role:
            return qs
        if user.is_teacher:
            return qs.filter(Q(status=Course.Status.PUBLISHED) | Q(teacher=user))
    return qs.filter(status=Course.Status.PUBLISHED)


def can_access_course_content(user, course: Course) -> bool:
    if user.is_authenticated:
        if user.is_admin_role or course.teacher_id == user.id:
            return True
        if user.is_student and course.status == Course.Status.PUBLISHED:
            from apps.enrollments.models import Enrollment

            return Enrollment.objects.filter(student=user, course=course).exists()
    return False
