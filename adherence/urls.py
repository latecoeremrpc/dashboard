from django.urls import path
from adherence import views 

urlpatterns = [
    path('adherence', views.home, name='adhrencemexep'),
    path('calcul', views.calcul, name='adhrencemexepcalcul'),
]



