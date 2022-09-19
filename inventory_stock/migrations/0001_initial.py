# Generated by Django 4.0.1 on 2022-09-13 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MaterialSheet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(null=True)),
                ('week', models.IntegerField(null=True)),
                ('material', models.CharField(max_length=30, null=True)),
                ('division', models.CharField(max_length=30, null=True)),
                ('material_type', models.CharField(max_length=30, null=True)),
                ('individual_collective', models.CharField(max_length=30, null=True)),
                ('standard_price', models.FloatField(null=True)),
                ('pr_moy_pond', models.FloatField(null=True)),
                ('price_basis', models.FloatField(null=True)),
                ('company', models.CharField(max_length=30, null=True)),
                ('currency', models.FloatField(null=True)),
                ('ps_unit_div', models.FloatField(null=True)),
                ('pmp_unit_div', models.FloatField(null=True)),
                ('ps_unit_euro', models.FloatField(null=True)),
                ('pmp_unit_euro', models.FloatField(null=True)),
                ('stock', models.FloatField(null=True)),
                ('lot_qm', models.FloatField(null=True)),
                ('stock_transit', models.FloatField(null=True)),
                ('stock_blocked', models.FloatField(null=True)),
                ('valuation_ps_div', models.FloatField(null=True)),
                ('valuation_pmp_div', models.FloatField(null=True)),
                ('valuation_ps_euro', models.FloatField(null=True)),
                ('valuation_pmp_euro', models.FloatField(null=True)),
            ],
        ),
    ]
