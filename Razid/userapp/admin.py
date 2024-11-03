from django.contrib import admin
from  .models import Rating,OrderPlaced
# Register your models here.
admin.site.register(Rating)
admin.site.register(OrderPlaced)