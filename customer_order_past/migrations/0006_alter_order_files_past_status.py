# Generated by Django 4.0.1 on 2023-01-26 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer_order_past', '0005_alter_order_files_remarque1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order_files',
            name='past_status',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
