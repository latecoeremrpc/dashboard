from unicodedata import name
from django.urls import path
from purchasepast import views

urlpatterns = [
    path('', views.home,name='PurchasePastHome'),
    path('calcul', views.upload_files,name='PurchasePastcalcul'),
    path('details/' , views.details, name='PurchasePastdetails'),

]