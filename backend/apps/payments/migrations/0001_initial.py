import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0003_course_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='KZT', max_length=3)),
                ('status', models.CharField(choices=[('pending', 'Ожидает оплаты'), ('paid', 'Оплачен'), ('failed', 'Не оплачен'), ('cancelled', 'Отменен')], default='pending', max_length=20)),
                ('provider', models.CharField(choices=[('freedompay', 'Freedom Pay')], default='freedompay', max_length=30)),
                ('provider_payment_id', models.CharField(blank=True, max_length=100)),
                ('provider_redirect_url', models.URLField(blank=True)),
                ('order_id', models.CharField(max_length=50, unique=True)),
                ('failure_reason', models.TextField(blank=True)),
                ('raw_callback', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payments', to='courses.course')),
                ('student', models.ForeignKey(limit_choices_to={'role': 'student'}, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['student', '-created_at'], name='payments_pa_student_7407eb_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['status', '-created_at'], name='payments_pa_status_23f8c5_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['order_id'], name='payments_pa_order_i_f6e1b3_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['provider_payment_id'], name='payments_pa_provide_2dc293_idx'),
        ),
    ]

