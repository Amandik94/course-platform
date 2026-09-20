from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('payments', '0002_add_paybot_support'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='currency',
            field=models.CharField(default='RUB', max_length=3),
        ),
        migrations.AlterField(
            model_name='payment',
            name='provider',
            field=models.CharField(
                choices=[
                    ('freedompay', 'Freedom Pay'),
                    ('paybot', 'PayBot (архив)'),
                    ('yookassa', 'YooKassa'),
                ],
                default='yookassa',
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name='processedwebhook',
            name='provider',
            field=models.CharField(
                choices=[
                    ('freedompay', 'Freedom Pay'),
                    ('paybot', 'PayBot (архив)'),
                    ('yookassa', 'YooKassa'),
                ],
                max_length=30,
            ),
        ),
    ]
