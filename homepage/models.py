from django.db import models

# Create your models here.

class HomeKpi(models.Model):
    username=models.CharField(max_length=20)
    kpi=models.CharField(max_length=100)
    theme=models.CharField(max_length=100,null=True)
    col=models.IntegerField(null=True)




    def __str__(self):
        return format(self.username+' / ')+format(self.theme+' / ')+format(self.kpi)
