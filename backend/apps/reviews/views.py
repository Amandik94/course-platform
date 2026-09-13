from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from apps.courses.access import visible_courses_for_user
from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from apps.notifications.models import Notification
from apps.notifications.services import create_notification

from .models import Review
from .permissions import IsReviewOwnerOrAdminDeleteOrReadOnly
from .serializers import ReviewSerializer


def get_visible_course_for_request(request, course_id):
    return get_object_or_404(visible_courses_for_user(request.user), id=course_id)


@extend_schema_view(
    get=extend_schema(tags=['Отзывы'], summary='Список отзывов курса'),
    post=extend_schema(tags=['Отзывы'], summary='Создать отзыв о курсе'),
)
class CourseReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()
        course = get_visible_course_for_request(self.request, self.kwargs['course_id'])
        return Review.objects.filter(course=course).select_related('student', 'course')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if not getattr(self, 'swagger_fake_view', False):
            context['course'] = get_visible_course_for_request(
                self.request,
                self.kwargs['course_id'],
            )
        return context

    def perform_create(self, serializer):
        user = self.request.user
        course = get_visible_course_for_request(self.request, self.kwargs['course_id'])

        if not user.is_student:
            raise PermissionDenied('Оставлять отзывы могут только студенты.')
        if not Enrollment.objects.filter(student=user, course=course).exists():
            raise PermissionDenied('Вы можете оставить отзыв только после записи на курс.')

        review = serializer.save(course=course, student=user)
        create_notification(
            user=course.teacher,
            type=Notification.Type.COURSE,
            title=f'Новый отзыв о курсе «{course.title}»',
            message=f'{user.full_name or user.email} поставил(а) оценку {review.rating}/5.',
            link=f'/courses/{course.id}',
            metadata={'review_id': review.id, 'course_id': course.id},
        )


@extend_schema_view(
    get=extend_schema(tags=['Отзывы'], summary='Получить отзыв'),
    patch=extend_schema(tags=['Отзывы'], summary='Обновить свой отзыв'),
    delete=extend_schema(tags=['Отзывы'], summary='Удалить свой отзыв'),
)
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewOwnerOrAdminDeleteOrReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()

        visible_courses = visible_courses_for_user(self.request.user)
        queryset = Review.objects.select_related('student', 'course')

        if not self.request.user.is_authenticated:
            return queryset.filter(course__in=visible_courses)

        if self.request.user.is_admin_role:
            return queryset

        return queryset.filter(
            Q(course__in=visible_courses) | Q(student=self.request.user)
        )
