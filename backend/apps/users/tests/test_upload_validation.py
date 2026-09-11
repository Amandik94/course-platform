from io import BytesIO

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from config.validators import validate_image_upload


def make_image_file(name='avatar.png', content_type='image/png'):
    buffer = BytesIO()
    Image.new('RGB', (8, 8), color='white').save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type=content_type)


def test_valid_image_upload_passes():
    validate_image_upload(make_image_file())


@pytest.mark.parametrize(
    ('name', 'content_type', 'content'),
    [
        ('avatar.exe', 'application/octet-stream', b'MZ fake executable'),
        ('avatar.png', 'text/plain', b'not an image'),
    ],
)
def test_invalid_image_upload_rejected(name, content_type, content):
    upload = SimpleUploadedFile(name, content, content_type=content_type)

    with pytest.raises(ValidationError):
        validate_image_upload(upload)


def test_oversized_image_upload_rejected(settings):
    settings.MAX_IMAGE_UPLOAD_SIZE = 10

    with pytest.raises(ValidationError):
        validate_image_upload(make_image_file())
