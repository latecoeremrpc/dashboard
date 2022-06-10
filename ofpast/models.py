from django.db import models

# Create your models here.


class Koc4(models.Model):
    year=models.IntegerField()
    week=models.IntegerField()
    order=models.CharField(max_length=20,null=True)	
    material=models.CharField(max_length=20,null=True)
    cost_budget=models.FloatField(null=True)
    cost_real=models.FloatField(null=True)
    currency=models.CharField(max_length=10,null=True)	
    quantity_produced_plan=models.FloatField(null=True)	
    quantity_produced_real=models.FloatField(null=True)		
    unit=models.CharField(max_length=10,null=True)


class Coois(models.Model):
    year=models.IntegerField()
    week=models.IntegerField()
    profit_centre=models.CharField(max_length=20,null=True)
    order=models.CharField(max_length=20,null=True)
    division=models.CharField(max_length=20,null=True)
    material=models.CharField(max_length=20,null=True)
    designation=models.CharField(max_length=100,null=True)
    order_type=models.CharField(max_length=20,null=True)
    otp_element=models.CharField(max_length=20,null=True)
    manufacturing_version=models.CharField(max_length=20,null=True)
    system_status=models.CharField(max_length=100,null=True)
    customer_order=models.CharField(max_length=20,null=True)
    range_operations_number=models.CharField(max_length=20,null=True)
    entered_by=models.CharField(max_length=20,null=True)
    nomenclature_status=models.CharField(max_length=20,null=True)
    fixation=models.CharField(max_length=20,null=True)
    order_quantity=models.FloatField(null=True)
    delivered_quantity=models.FloatField(null=True)
    confirmed_scrapmodels=models.CharField(max_length=20,null=True)
    date_end_real=models.DateField(null=True)
    date_end_plan=models.DateField(null=True)
    date_start_plan=models.DateField(null=True)
    date_plan_opening=models.DateField(null=True) 
    date_request=models.DateField(null=True)
    date_entry=models.DateField(null=True)


