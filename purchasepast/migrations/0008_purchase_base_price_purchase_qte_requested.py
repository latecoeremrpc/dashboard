# Generated by Django 4.0.1 on 2022-10-07 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchasepast', '0007_purchase_material_purchase_supplier'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='base_price',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='purchase',
            name='qte_requested',
            field=models.FloatField(null=True),
        ),
    ]