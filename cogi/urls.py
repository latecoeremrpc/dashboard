from unicodedata import name
from django.urls import path
from cogi import views

urlpatterns = [
    path('', views.home,name='cogihome'),
    path('calcul', views.upload_files,name='cogicalcul'),
    path('details', views.details,name='cogidetails'),
]