# Generated by Django 4.0.1 on 2022-09-22 15:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_stock', '0005_remove_materialsheet_pmp_unit_div_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='materialsheet',
            name='price_basis',
        ),
    ]
