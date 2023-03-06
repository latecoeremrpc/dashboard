from django.contrib import admin
from customer_order_past.models import *

admin.site.register(Order_files)
admin.site.register(Order_past_per_divsion)
admin.site.register(Order_past_per_organisme)
admin.site.register(Order_past_per_cp)
admin.site.register(Order_past_per_errors)
