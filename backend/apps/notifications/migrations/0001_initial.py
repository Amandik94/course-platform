from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('course', 'Course'), ('lesson', 'Lesson'), ('assignment', 'Assignment'), ('submission', 'Submission'), ('quiz', 'Quiz'), ('certificate', 'Certificate'), ('system', 'System')], default='system', max_length=32)),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField(blank=True)),
                ('link', models.CharField(blank=True, max_length=255)),
                ('is_read', models.BooleanField(default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['user', 'is_read'], name='notificatio_user_id_f3109a_idx'),
                    models.Index(fields=['user', '-created_at'], name='notificatio_user_id_99242b_idx'),
                ],
            },
        ),
    ]
