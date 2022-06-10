from django.db import models

# Create your models here.


class Cogi(models.Model):
    year=models.IntegerField(null=True)
    week=models.IntegerField(null=True)
    treatment_status=models.CharField(max_length=100,null=True)
    stock_movement_doc=models.CharField(max_length=100,null=True)
    created_on=models.DateField(null=True)
    time=models.TimeField(null=True)
    error_date=models.DateField(null=True)
    time_error=models.TimeField(null=True)
    message_number=models.CharField(max_length=100,null=True)
    movement_code=models.CharField(max_length=100,null=True)
    error_text=models.CharField(max_length=200,null=True)
    material=models.CharField(max_length=100,null=True)
    division=models.CharField(max_length=100,null=True)
    store=models.CharField(max_length=100,null=True)
    order=models.CharField(max_length=100,null=True)
    customer_order=models.CharField(max_length=100,null=True)
    customer_order_item=models.CharField(max_length=100,null=True)
    otp_element=models.CharField(max_length=100,null=True)
    qty_unit_entered=models.CharField(max_length=100,null=True)

