"""dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('homepage.urls')),  
    path('dashboard/planification/adherencemexep/', include('adherence.urls')),   
    path('dashboard/manufacturing/ofpast/', include('ofpast.urls')),   
    path('dashboard/procurement/purchasepast/', include('purchasepast.urls')),   
    path('dashboard/mrpc/intercopurchase/', include('intercopurchase.urls')),   
    path('dashboard/logistics/cogi/', include('cogi.urls')),
    path('dashboard/convertpdf/', include('convertpdf.urls')),
    path('dashboard/inventory_accuracy/', include('inventory_accuracy.urls')),

]
