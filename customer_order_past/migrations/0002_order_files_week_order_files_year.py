# Generated by Django 4.0.1 on 2023-01-26 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer_order_past', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order_files',
            name='week',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='order_files',
            name='year',
            field=models.IntegerField(null=True),
        ),
    ]