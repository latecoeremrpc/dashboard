from django.db import models

# Create your models here.


class Purchase(models.Model):
    year=models.IntegerField(null=True)
    week=models.IntegerField(null=True)
    purchase_requisition=models.CharField(null=True,max_length=50)
    item_of_requisition=models.CharField(null=True,max_length=10)
    deletion_indicator=models.CharField(null=True,max_length=20)
    purchasing_group=models.CharField(null=True,max_length=20)
    material=models.CharField(null=True,max_length=20)
    division=models.CharField(null=True,max_length=20)
    transferring_division=models.CharField(null=True,max_length=20)
    requisition_date=models.DateField(null=True)
    release_date=models.DateField(null=True)
    valuation_price=models.FloatField(null=True)
    supplier=models.CharField(null=True,max_length=20)
    outline_agreement=models.CharField(null=True,max_length=20)
    principal_agmt_item=models.CharField(null=True,max_length=20)
    purchase_order=models.CharField(null=True,max_length=20)
    purchase_order_item=models.CharField(null=True,max_length=20)

