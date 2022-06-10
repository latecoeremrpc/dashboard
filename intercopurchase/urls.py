from unicodedata import name
from django.urls import path
from intercopurchase import views

urlpatterns = [
    path('', views.home,name='intercopurchaseHome'),
    path('calcul', views.upload_files,name='intercopurchaseCalcul'),
    path('details/' , views.details, name='intercopurchaseDetails'),

]