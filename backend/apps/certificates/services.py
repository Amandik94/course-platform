import io

from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.utils import timezone
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from .models import Certificate


CERTIFICATE_NUMBER_RETRIES = 5


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

    page.setFont('Helvetica-Bold', 28)
    page.drawCentredString(width / 2, height - 4 * cm, 'CERTIFICATE')

    page.setFont('Helvetica', 14)
    page.drawCentredString(width / 2, height - 6 * cm, 'This certifies that')

    page.setFont('Helvetica-Bold', 22)
    page.drawCentredString(width / 2, height - 8 * cm, student_name)

    page.setFont('Helvetica', 14)
    page.drawCentredString(width / 2, height - 9.5 * cm, 'has successfully completed the course')

    page.setFont('Helvetica-Bold', 18)
    page.drawCentredString(width / 2, height - 11 * cm, course_title)

    page.setFont('Helvetica', 10)
    page.drawString(2 * cm, 2 * cm, f'Number: {certificate_number}')
    page.drawRightString(width - 2 * cm, 2 * cm, f'Issued: {issued_date}')

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

    raise IntegrityError('Could not generate a unique certificate number.')
