import django_filters

from .models import Course


class CourseFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug')
    level = django_filters.ChoiceFilter(choices=Course.Level.choices)

    class Meta:
        model = Course
        fields = ['category', 'level']