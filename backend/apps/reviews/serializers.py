from rest_framework import serializers

from .models import Review


class ReviewAuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    avatar = serializers.ImageField(read_only=True)


class ReviewSerializer(serializers.ModelSerializer):
    student = ReviewAuthorSerializer(read_only=True)

    class Meta:
        model = Review
        fields = (
            'id',
            'student',
            'rating',
            'comment',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'student', 'created_at', 'updated_at')

    def validate_comment(self, value):
        comment = value.strip()
        if len(comment) < 10:
            raise serializers.ValidationError('Комментарий должен быть не короче 10 символов.')
        if len(comment) > 2000:
            raise serializers.ValidationError('Комментарий не должен превышать 2000 символов.')
        return comment

    def validate(self, attrs):
        request = self.context.get('request')
        course = self.context.get('course')

        if request and course and request.method == 'POST':
            if Review.objects.filter(course=course, student=request.user).exists():
                raise serializers.ValidationError({
                    'detail': 'Вы уже оставили отзыв на этот курс.'
                })

        return attrs
