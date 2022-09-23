from django.urls import path
from inventory_stock import views

urlpatterns = [
    path('', views.home, name='inventory_stockhome'),
    path('upload/', views.upload_files, name='inventory_stockupload'),
    path('details/', views.details, name='inventory_stockdetails'),
    # path('tables/', views.tables, name='inventory_stocktables'),
]