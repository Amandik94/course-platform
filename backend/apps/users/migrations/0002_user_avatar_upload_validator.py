from django.db import migrations, models

import config.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='avatars/',
                validators=[config.validators.validate_image_upload],
                verbose_name='Аватар',
            ),
        ),
    ]
