from decimal import Decimal

from django.db import migrations


PRICE_CHANGES = {
    5: (Decimal('4990.00'), Decimal('1490.00')),
    6: (Decimal('7990.00'), Decimal('1990.00')),
    7: (Decimal('9990.00'), Decimal('2490.00')),
    8: (Decimal('6990.00'), Decimal('1990.00')),
    9: (Decimal('12990.00'), Decimal('2990.00')),
    10: (Decimal('7990.00'), Decimal('1990.00')),
    11: (Decimal('4990.00'), Decimal('990.00')),
    12: (Decimal('8990.00'), Decimal('2490.00')),
    13: (Decimal('14990.00'), Decimal('3990.00')),
}


def set_rub_demo_prices(apps, schema_editor):
    Course = apps.get_model('courses', 'Course')
    for course_id, (old_price, new_price) in PRICE_CHANGES.items():
        Course.objects.filter(pk=course_id, price=old_price).update(price=new_price)


def restore_kzt_demo_prices(apps, schema_editor):
    Course = apps.get_model('courses', 'Course')
    for course_id, (old_price, new_price) in PRICE_CHANGES.items():
        Course.objects.filter(pk=course_id, price=new_price).update(price=old_price)


class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0003_course_price'),
    ]

    operations = [
        migrations.RunPython(set_rub_demo_prices, restore_kzt_demo_prices),
    ]
