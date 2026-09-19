import pytest
from django.urls import reverse
from rest_framework import status

from apps.enrollments.models import Enrollment
from apps.reviews.models import Review


@pytest.mark.django_db
class TestCourseReviews:
    def test_anonymous_can_list_public_course_reviews(self, api_client, published_course, student_user):
        Review.objects.create(
            course=published_course,
            student=student_user,
            rating=5,
            comment='This course was very useful.',
        )

        response = api_client.get(reverse('course-review-list', kwargs={'course_id': published_course.id}))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['rating'] == 5
        assert 'email' not in response.data['results'][0]['student']

    def test_anonymous_cannot_create_review(self, api_client, published_course):
        response = api_client.post(
            reverse('course-review-list', kwargs={'course_id': published_course.id}),
            {'rating': 5, 'comment': 'Great course with practical lessons.'},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_enrolled_student_can_create_review(self, student_client, student_user, published_course):
        Enrollment.objects.create(student=student_user, course=published_course)

        response = student_client.post(
            reverse('course-review-list', kwargs={'course_id': published_course.id}),
            {'rating': 5, 'comment': 'Great course with practical lessons.'},
        )

        assert response.status_code == status.HTTP_201_CREATED
        review = Review.objects.get(course=published_course, student=student_user)
        assert review.rating == 5

    def test_non_enrolled_student_cannot_create_review(self, student_client, published_course):
        response = student_client.post(
            reverse('course-review-list', kwargs={'course_id': published_course.id}),
            {'rating': 5, 'comment': 'Great course with practical lessons.'},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Review.objects.count() == 0

    def test_duplicate_review_rejected(self, student_client, student_user, published_course):
        Enrollment.objects.create(student=student_user, course=published_course)
        Review.objects.create(
            course=published_course,
            student=student_user,
            rating=4,
            comment='The first review is already here.',
        )

        response = student_client.post(
            reverse('course-review-list', kwargs={'course_id': published_course.id}),
            {'rating': 5, 'comment': 'Trying to review this course twice.'},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Review.objects.filter(course=published_course, student=student_user).count() == 1

    def test_mine_filter_returns_only_current_students_review(
        self, student_client, student_user, published_course, django_user_model,
    ):
        other_student = django_user_model.objects.create_user(
            email='other-filtered-reviewer@test.com', password='pass12345', role='student',
        )
        own_review = Review.objects.create(
            course=published_course,
            student=student_user,
            rating=5,
            comment='My existing review text.',
        )
        Review.objects.create(
            course=published_course,
            student=other_student,
            rating=4,
            comment='Another student review text.',
        )

        response = student_client.get(
            reverse('course-review-list', kwargs={'course_id': published_course.id}),
            {'mine': 'true'},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['id'] == own_review.id

    @pytest.mark.parametrize('rating', [0, 6])
    def test_invalid_rating_rejected(self, student_client, student_user, published_course, rating):
        Enrollment.objects.create(student=student_user, course=published_course)

        response = student_client.post(
            reverse('course-review-list', kwargs={'course_id': published_course.id}),
            {'rating': rating, 'comment': 'This comment is long enough.'},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_student_cannot_spoof_student_or_course(self, student_client, student_user, published_course, category, teacher_user, django_user_model):
        other_student = django_user_model.objects.create_user(
            email='other-student@test.com',
            password='pass12345',
            role='student',
        )
        other_course = published_course.__class__.objects.create(
            title='Other Course',
            short_description='...',
            description='...',
            category=category,
            teacher=teacher_user,
            status=published_course.Status.PUBLISHED,
        )
        Enrollment.objects.create(student=student_user, course=published_course)

        response = student_client.post(
            reverse('course-review-list', kwargs={'course_id': published_course.id}),
            {
                'rating': 5,
                'comment': 'The payload should not decide ownership.',
                'student': {'id': other_student.id},
                'course': other_course.id,
            },
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        review = Review.objects.get()
        assert review.student == student_user
        assert review.course == published_course


@pytest.mark.django_db
class TestReviewObjectPermissions:
    def test_owner_can_update_review(self, student_client, student_user, published_course):
        review = Review.objects.create(
            course=published_course,
            student=student_user,
            rating=4,
            comment='Original review text.',
        )

        response = student_client.patch(
            reverse('review-detail', kwargs={'pk': review.id}),
            {'rating': 5, 'comment': 'Updated review text.'},
        )

        assert response.status_code == status.HTTP_200_OK
        review.refresh_from_db()
        assert review.rating == 5
        assert review.comment == 'Updated review text.'

    def test_foreign_student_cannot_update_review(self, api_client, student_user, published_course, django_user_model):
        other_student = django_user_model.objects.create_user(
            email='other-reviewer@test.com',
            password='pass12345',
            role='student',
        )
        review = Review.objects.create(
            course=published_course,
            student=student_user,
            rating=4,
            comment='Original review text.',
        )
        api_client.force_authenticate(user=other_student)

        response = api_client.patch(
            reverse('review-detail', kwargs={'pk': review.id}),
            {'rating': 1, 'comment': 'Malicious update text.'},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        review.refresh_from_db()
        assert review.rating == 4

    def test_owner_can_delete_review(self, student_client, student_user, published_course):
        review = Review.objects.create(
            course=published_course,
            student=student_user,
            rating=4,
            comment='Original review text.',
        )

        response = student_client.delete(reverse('review-detail', kwargs={'pk': review.id}))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Review.objects.filter(id=review.id).exists()

    def test_foreign_student_cannot_delete_review(self, api_client, student_user, published_course, django_user_model):
        other_student = django_user_model.objects.create_user(
            email='other-deleter@test.com',
            password='pass12345',
            role='student',
        )
        review = Review.objects.create(
            course=published_course,
            student=student_user,
            rating=4,
            comment='Original review text.',
        )
        api_client.force_authenticate(user=other_student)

        response = api_client.delete(reverse('review-detail', kwargs={'pk': review.id}))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Review.objects.filter(id=review.id).exists()

    def test_teacher_cannot_alter_student_review(self, teacher_client, student_user, published_course):
        review = Review.objects.create(
            course=published_course,
            student=student_user,
            rating=2,
            comment='A critical but valid student review.',
        )

        response = teacher_client.patch(
            reverse('review-detail', kwargs={'pk': review.id}),
            {'rating': 5, 'comment': 'Changed by teacher.'},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_delete_review_for_moderation(self, admin_client, student_user, published_course):
        review = Review.objects.create(
            course=published_course,
            student=student_user,
            rating=1,
            comment='A review that admin decided to moderate.',
        )

        response = admin_client.delete(reverse('review-detail', kwargs={'pk': review.id}))

        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestCourseRatingAggregation:
    def test_course_detail_includes_average_rating_and_count(self, api_client, published_course, student_user, django_user_model):
        other_student = django_user_model.objects.create_user(
            email='rating-user@test.com',
            password='pass12345',
            role='student',
        )
        Review.objects.create(
            course=published_course,
            student=student_user,
            rating=5,
            comment='Excellent course content.',
        )
        Review.objects.create(
            course=published_course,
            student=other_student,
            rating=3,
            comment='Good but could be deeper.',
        )

        response = api_client.get(reverse('course-detail', kwargs={'id': published_course.id}))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['average_rating'] == 4.0
        assert response.data['reviews_count'] == 2

    def test_course_without_reviews_has_zero_rating(self, api_client, published_course):
        response = api_client.get(reverse('course-detail', kwargs={'id': published_course.id}))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['average_rating'] == 0.0
        assert response.data['reviews_count'] == 0
