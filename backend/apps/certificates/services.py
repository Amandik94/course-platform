import io
from pathlib import Path

from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.utils import timezone
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .models import Certificate


CERTIFICATE_NUMBER_RETRIES = 5
CYRILLIC_FONT_NAME = 'DejaVuSans'


def _get_certificate_font() -> str:
    font_paths = [
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
        Path('/usr/local/share/fonts/DejaVuSans.ttf'),
        Path('C:/Windows/Fonts/arial.ttf'),
    ]
    if CYRILLIC_FONT_NAME in pdfmetrics.getRegisteredFontNames():
        return CYRILLIC_FONT_NAME
    for font_path in font_paths:
        if font_path.exists():
            pdfmetrics.registerFont(TTFont(CYRILLIC_FONT_NAME, str(font_path)))
            return CYRILLIC_FONT_NAME
    return 'Helvetica'


def _generate_certificate_number() -> str:
    year = timezone.now().year
    prefix = f'LMS-{year}-'
    last = (
        Certificate.objects.filter(certificate_number__startswith=prefix)
        .order_by('-certificate_number')
        .first()
    )
    next_number = 1
    if last:
        next_number = int(last.certificate_number.split('-')[-1]) + 1
    return f'{prefix}{next_number:06d}'


def _render_pdf(student_name: str, course_title: str, certificate_number: str, issued_date: str) -> bytes:
    buffer = io.BytesIO()
    page = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    font_name = _get_certificate_font()

    page.setFont(font_name, 28)
    page.drawCentredString(width / 2, height - 4 * cm, 'СЕРТИФИКАТ')

    page.setFont(font_name, 14)
    page.drawCentredString(width / 2, height - 6 * cm, 'Настоящим подтверждается, что')

    page.setFont(font_name, 22)
    page.drawCentredString(width / 2, height - 8 * cm, student_name)

    page.setFont(font_name, 14)
    page.drawCentredString(width / 2, height - 9.5 * cm, 'успешно завершил(а) курс')

    page.setFont(font_name, 18)
    page.drawCentredString(width / 2, height - 11 * cm, course_title)

    page.setFont(font_name, 10)
    page.drawString(2 * cm, 2 * cm, f'Номер: {certificate_number}')
    page.drawRightString(width - 2 * cm, 2 * cm, f'Дата выдачи: {issued_date}')

    page.showPage()
    page.save()
    buffer.seek(0)
    return buffer.read()


def _create_certificate_with_pdf(student, course) -> Certificate:
    certificate_number = _generate_certificate_number()
    certificate = Certificate.objects.create(
        student=student,
        course=course,
        certificate_number=certificate_number,
    )

    pdf_bytes = _render_pdf(
        student_name=student.full_name or student.email,
        course_title=course.title,
        certificate_number=certificate_number,
        issued_date=certificate.issued_at.strftime('%d.%m.%Y'),
    )
    certificate.pdf.save(f'{certificate_number}.pdf', ContentFile(pdf_bytes), save=True)
    return certificate


def issue_certificate(student, course) -> Certificate:
    for _ in range(CERTIFICATE_NUMBER_RETRIES):
        try:
            with transaction.atomic():
                existing = Certificate.objects.filter(student=student, course=course).first()
                if existing:
                    return existing
                return _create_certificate_with_pdf(student, course)
        except IntegrityError:
            existing = Certificate.objects.filter(student=student, course=course).first()
            if existing:
                return existing

    raise IntegrityError('Не удалось сгенерировать уникальный номер сертификата.')
