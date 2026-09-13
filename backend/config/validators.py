import os

from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image


ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
ALLOWED_IMAGE_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}


def validate_image_upload(uploaded_file):
    max_size = getattr(settings, 'MAX_IMAGE_UPLOAD_SIZE', 2 * 1024 * 1024)
    if uploaded_file.size > max_size:
        raise ValidationError(f'Размер изображения не должен превышать {max_size // (1024 * 1024)} МБ.')

    extension = os.path.splitext(uploaded_file.name)[1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError('Неподдерживаемое расширение изображения.')

    content_type = getattr(uploaded_file, 'content_type', None)
    if content_type and content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise ValidationError('Неподдерживаемый MIME-тип изображения.')

    position = uploaded_file.tell() if hasattr(uploaded_file, 'tell') else None
    try:
        image = Image.open(uploaded_file)
        image.verify()
    except Exception as exc:
        raise ValidationError('Файл не является корректным изображением.') from exc
    finally:
        if position is not None:
            uploaded_file.seek(position)
