from rest_framework import serializers


class QuizResultItemSerializer(serializers.Serializer):
    quiz_title = serializers.CharField()
    score = serializers.IntegerField()
    passed = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class StudentDashboardSerializer(serializers.Serializer):
    active_courses_count = serializers.IntegerField()
    completed_courses_count = serializers.IntegerField()
    average_progress = serializers.IntegerField()
    certificates_count = serializers.IntegerField()
    recent_quiz_results = QuizResultItemSerializer(many=True)


class TeacherCourseSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    students_count = serializers.IntegerField()
    status = serializers.CharField()


class TeacherDashboardSerializer(serializers.Serializer):
    courses_count = serializers.IntegerField()
    students_count = serializers.IntegerField()
    pending_submissions_count = serializers.IntegerField()
    courses = TeacherCourseSummarySerializer(many=True)


class AdminDashboardSerializer(serializers.Serializer):
    users_count = serializers.IntegerField()
    students_count = serializers.IntegerField()
    teachers_count = serializers.IntegerField()
    courses_count = serializers.IntegerField()
    active_courses_count = serializers.IntegerField()
    completed_enrollments_count = serializers.IntegerField()
    average_progress = serializers.IntegerField()