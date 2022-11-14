from unicodedata import name
from django.urls import path
from ofpast import views

urlpatterns = [
    path('', views.home,name='ofpasthome'),
    path('calcul', views.upload_files,name='ofpastcalcul'),
    path('details/' , views.details, name='ofpastdetails'),
    path('download/' , views.download, name='ofpastdownload'),
    # path('details/download' , views.details, name='ofpastdetailsdownload'),
    path('calendar' , views.calendar, name='calendar'), #To delete

]