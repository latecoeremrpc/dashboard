# Generated by Django 4.0.1 on 2022-03-04 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchasepast', '0005_alter_purchase_transferring_division'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='transferring_division',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
