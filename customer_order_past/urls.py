from django.urls import path
from customer_order_past import views


urlpatterns = [
    path('', views.home,name='CustomerOrderPastHome'),
    path('calcul', views.upload_files,name='CustomerOrdercalcul'),

    
]
