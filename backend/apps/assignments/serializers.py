from rest_framework import serializers

from .models import Assignment, AssignmentSubmission


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = (
            'id', 'lesson', 'title', 'description', 'starter_code',
            'max_score', 'deadline',
        )
        read_only_fields = ('lesson',)


class SubmitAssignmentSerializer(serializers.Serializer):
    """Для POST /assignments/{id}/submit/ — принимает только код решения."""
    code = serializers.CharField()


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    """Для студента — просмотр своего решения (без списка чужих)."""
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = (
            'id', 'assignment', 'student', 'student_name', 'code',
            'status', 'score', 'teacher_comment', 'created_at', 'updated_at',
        )
        read_only_fields = ('assignment', 'student', 'status', 'score', 'teacher_comment')
        # студент не может сам себе выставить оценку или сменить статус


class SubmissionReviewSerializer(serializers.ModelSerializer):
    """Для преподавателя — проверка решения (может менять status/score/comment)."""
    class Meta:
        model = AssignmentSubmission
        fields = ('id', 'status', 'score', 'teacher_comment')

    def validate(self, attrs):
        status = attrs.get('status', getattr(self.instance, 'status', None))
        score = attrs.get('score', getattr(self.instance, 'score', None))
        max_score = self.instance.assignment.max_score if self.instance else None

        if status == AssignmentSubmission.Status.ACCEPTED and score is None:
            raise serializers.ValidationError({'score': 'При статусе accepted нужно указать оценку'})
        if score is not None and max_score is not None and score > max_score:
            raise serializers.ValidationError({'score': f'Оценка не может превышать {max_score}'})
        return attrs