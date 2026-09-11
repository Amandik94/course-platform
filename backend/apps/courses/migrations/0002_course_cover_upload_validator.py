from django.db import migrations, models

import config.validators


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='cover',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='courses/covers/',
                validators=[config.validators.validate_image_upload],
            ),
        ),
    ]
