import io

from django.core.files.base import ContentFile
from django.db import transaction
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from .models import Certificate


def _generate_certificate_number() -> str:
    """
    Формат: LMS-<год>-<инкремент с ведущими нулями>.
    Например: LMS-2026-000001
    """
    from django.utils import timezone
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
    """
    Простая генерация PDF через reportlab: заголовок, имя студента,
    название курса, номер сертификата и дата. Без QR-кода (следующий этап).
    """
    buffer = io.BytesIO()
    page = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    page.setFont('Helvetica-Bold', 28)
    page.drawCentredString(width / 2, height - 4 * cm, 'СЕРТИФИКАТ')

    page.setFont('Helvetica', 14)
    page.drawCentredString(width / 2, height - 6 * cm, 'настоящим подтверждается, что')

    page.setFont('Helvetica-Bold', 22)
    page.drawCentredString(width / 2, height - 8 * cm, student_name)

    page.setFont('Helvetica', 14)
    page.drawCentredString(width / 2, height - 9.5 * cm, 'успешно завершил(а) курс')

    page.setFont('Helvetica-Bold', 18)
    page.drawCentredString(width / 2, height - 11 * cm, course_title)

    page.setFont('Helvetica', 10)
    page.drawString(2 * cm, 2 * cm, f'Номер: {certificate_number}')
    page.drawRightString(width - 2 * cm, 2 * cm, f'Дата выдачи: {issued_date}')

    page.showPage()
    page.save()
    buffer.seek(0)
    return buffer.read()


@transaction.atomic
def issue_certificate(student, course) -> Certificate:
    """
    Создаёт сертификат для студента по курсу, если его ещё нет.
    Идемпотентна: повторный вызов для уже выданного сертификата
    просто вернёт существующую запись, не создавая дубликат.
    """
    existing = Certificate.objects.filter(student=student, course=course).first()
    if existing:
        return existing

    certificate_number = _generate_certificate_number()
    certificate = Certificate.objects.create(
        student=student, course=course, certificate_number=certificate_number,
    )

    pdf_bytes = _render_pdf(
        student_name=student.full_name or student.email,
        course_title=course.title,
        certificate_number=certificate_number,
        issued_date=certificate.issued_at.strftime('%d.%m.%Y'),
    )
    certificate.pdf.save(f'{certificate_number}.pdf', ContentFile(pdf_bytes), save=True)
    return certificate