from django.db import models


# Result Table.
class Result(models.Model):
    week=models.IntegerField()
    year=models.IntegerField()
    division=models.IntegerField()
    profit_centre=models.CharField(max_length=50)
    order=models.CharField(max_length=50)
    material=models.CharField(max_length=50)
    designation=models.CharField(max_length=50,null=True)
    order_type=models.CharField(max_length=50,null=True)
    order_quantity=models.IntegerField()
    date_start_plan=models.DateField(null=True)	
    date_end_plan=models.DateField(null=True)	
    fixation=models.CharField(max_length=50,null=True)
    manager=models.CharField(max_length=50,null=True)
    order_stat=models.CharField(max_length=50,null=True)
    request=models.CharField(max_length=50,null=True)
    date_end_real=models.DateField(null=True)	
    entered_by=models.CharField(max_length=50,null=True)
    date_available=models.DateField(null=True)	
    date_reordo=models.DateField(null=True)	
    message=models.IntegerField(null=True)
    element=models.CharField(max_length=50,null=True)
    planning=models.CharField(max_length=50,null=True)
    type=models.CharField(max_length=50,null=True)
    H1_jo=models.IntegerField(null=True)
    H2_jo=models.IntegerField(null=True)
    H3_jo=models.IntegerField(null=True)
    H4_jo=models.IntegerField(null=True)
    H1_end=models.DateField()
    H2_end=models.DateField()
    H3_end=models.DateField()
    H4_end=models.DateField()
    H4_global_end=models.DateField()
    date_reference=models.DateField(null=True)
    H1=models.BooleanField(default=False)
    H2=models.BooleanField(default=False)
    H3=models.BooleanField(default=False)
    H4_global=models.BooleanField(default=False)
    after_H4_global=models.BooleanField(default=False)
    H1_M10=models.BooleanField(default=False)
    H1_M15=models.BooleanField(default=False)
    H1_M20=models.BooleanField(default=False)
    H1_unfix=models.BooleanField(default=False)
    H2_M10=models.BooleanField(default=False)
    H2_M15=models.BooleanField(default=False)
    H2_M20=models.BooleanField(default=False)
    H2_unfix=models.BooleanField(default=False)
    H3_M10=models.BooleanField(default=False)
    H3_M15=models.BooleanField(default=False)
    H3_M20=models.BooleanField(default=False)
    H3_unfix=models.BooleanField(default=False)
    after_H4_global_fix=models.BooleanField(default=False)
    profondeur=models.IntegerField()
    H1_10_P=models.BooleanField(default=False)
    H2_10_P=models.BooleanField(default=False)
    H3_10_P=models.BooleanField(default=False)
    H1_15_P=models.BooleanField(default=False)
    H2_15_P=models.BooleanField(default=False)
    H3_15_P=models.BooleanField(default=False)


    def __str__(self):
        data='Material: '+format(self.material), 'Order: '+format(self.order)
        return format(data) 




# Input files 
class Material(models.Model):
    week=models.IntegerField()
    year=models.IntegerField()
    profit_centre=models.CharField(max_length=50,null=True)
    material= models.CharField(max_length=50)
    division=models.IntegerField()
    manager=models.CharField(max_length=50,null=True)
    type=models.CharField(max_length=50,null=True)
    planning=models.CharField(max_length=50,null=True)
    comment=models.CharField(max_length=150,null=True)
    cycle_appro=models.IntegerField()
    cycle_manuf=models.IntegerField()	
    key_horizon=models.IntegerField()
    security_deadline=models.CharField(max_length=150,null=True)
    reception_time=models.CharField(max_length=150,null=True)


    # Show field on admin page
    # result must be a string use format function
    def __str__(self):
        return self.material



class Zpp(models.Model):
    material= models.CharField(max_length=50,null=True)
    date_available= models.DateField(null=True)	
    element= models.CharField(max_length=50,null=True)		
    order= models.CharField(max_length=50,null=True)	
    message= models.IntegerField(null=True)	
    date_reordo=models.DateField(null=True)
    week=models.IntegerField()
    year=models.IntegerField()
    division= models.CharField(max_length=50)	


    # Show field on admin page
    # result must be a string use format function
    def __str__(self):
        data='Material: '+format(self.material), 'Order: '+format(self.order)
        return format(data) 

class Coois(models.Model):
    week=models.IntegerField()
    year=models.IntegerField()
    division=models.IntegerField()
    profit_centre=models.CharField(max_length=50,null=True)
    order=models.CharField(max_length=50)
    material= models.CharField(max_length=50,null=True)
    designation=models.CharField(max_length=50,null=True)
    order_type=models.CharField(max_length=50,null=True)
    order_quantity=models.IntegerField()
    date_start_plan=models.DateField(null=True)	
    date_end_plan=models.DateField(null=True)	
    fixation=models.CharField(max_length=50,null=True)
    manager=models.CharField(max_length=50,null=True)
    order_stat=models.CharField(max_length=50,null=True)
    request=models.CharField(max_length=50,null=True)
    date_end_real=models.DateField(null=True)	
    entered_by=models.CharField(max_length=50,null=True)

    # Show field on admin page
    # result must be a string use format function
    def __str__(self):
        data='Material: '+format(self.material), 'Order: '+format(self.order)
        return format(data) 









