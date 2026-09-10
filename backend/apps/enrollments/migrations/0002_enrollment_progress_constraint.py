from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='enrollment',
            constraint=models.CheckConstraint(
                check=models.Q(progress__gte=0, progress__lte=100),
                name='enrollment_progress_0_100',
            ),
        ),
    ]
