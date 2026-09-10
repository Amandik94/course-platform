from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='quiz',
            constraint=models.CheckConstraint(
                check=models.Q(passing_score__gte=0, passing_score__lte=100),
                name='quiz_passing_score_0_100',
            ),
        ),
        migrations.AddConstraint(
            model_name='quizattempt',
            constraint=models.CheckConstraint(
                check=models.Q(score__gte=0, score__lte=100),
                name='quiz_attempt_score_0_100',
            ),
        ),
    ]
