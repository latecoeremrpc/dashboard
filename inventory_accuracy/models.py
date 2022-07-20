from asyncio.windows_events import NULL
from django.db import models

# Create your models here.
class SQ00(models.Model):
    year=models.IntegerField()
    week=models.IntegerField()
    inventory_doc=models.CharField(max_length=50, null=True)
    material=models.CharField(max_length=50,null=True)
    designation=models.CharField(max_length=50,null=True)
    type=models.CharField(max_length=10,null=True)
    unit=models.CharField(max_length=10,null=True)
    division=models.IntegerField()
    store=models.IntegerField(null=True)
    supplier=models.CharField(max_length=50, null=True)
    theoritical_quantity=models.DecimalField(max_digits=20, decimal_places=2,null=True)
    entred_quantity=models.DecimalField(max_digits=20, decimal_places=2,null=True)
    deviation=models.DecimalField(max_digits=20, decimal_places=2,null=True)
    deviation_cost=models.DecimalField(max_digits=20, decimal_places=2,null=True)
    dev=models.CharField(max_length=10,null=True)
    date_catchment=models.DateField(null=True)
    corrected_by=models.CharField(max_length=50,null=True)
    catchment=models.CharField(max_length=50,null=True)
    delete=models.CharField(max_length=10,null=True)
    refecrence_inventory=models.CharField(max_length=50,null=True)
    inventory_number=models.CharField(max_length=50,null=True)
    Tys=models.IntegerField(null=True)

    def __str__(self):
        return self.material