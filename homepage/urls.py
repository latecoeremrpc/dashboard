from django.urls import path
from homepage import views 

urlpatterns = [
    path('home/', views.homeview,name='homepage'),
    path('contact/', views.contact,name='contactpage'),
    path('home/settings', views.homesettings,name='homesettings'),
]