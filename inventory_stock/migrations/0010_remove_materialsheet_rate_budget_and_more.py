# Generated by Django 4.0.1 on 2023-01-02 08:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_stock', '0009_rename_rate_materialsheet_rate_budget_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='materialsheet',
            name='rate_budget',
        ),
        migrations.RemoveField(
            model_name='materialsheet',
            name='rate_last',
        ),
    ]
