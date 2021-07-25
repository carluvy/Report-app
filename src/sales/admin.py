from django.contrib import admin

# Register your models here.
from sales.models import Position, Sale, CSV

admin.site.register(Position)
admin.site.register(Sale)
admin.site.register(CSV)