from django.urls import path
from inventory_accuracy import views

urlpatterns = [
    path('', views.home, name='inventory_accuracyhome'),
    path('upload/', views.upload_files, name='inventory_accuracyupload'),
]
