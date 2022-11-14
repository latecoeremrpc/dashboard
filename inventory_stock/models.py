from django.db import models

# Create your models here.
class MaterialSheet(models.Model):
    year=models.IntegerField(null=True)
    week=models.IntegerField(null=True)
    material=models.CharField(max_length=30,null=True)
    division=models.CharField(max_length=30,null=True)
    profit_center=models.CharField(max_length=30,null=True)
    material_type=models.CharField(max_length=30,null=True)
    individual_collective=models.CharField(max_length=30,null=True)
    standard_price=models.FloatField(null=True)
    price_basis=models.FloatField(null=True)     
    pr_moy_pond=models.FloatField(null=True)
    company=models.CharField(max_length=30,null=True)
    currency=models.CharField(max_length=30,null=True)
    rate=models.FloatField(null=True) 
    stock=models.FloatField(null=True)
    returnable_stock=models.FloatField(null=True)
    lot_qm=models.FloatField(null=True)
    stock_transit=models.FloatField(null=True)
    stock_blocked=models.FloatField(null=True)

