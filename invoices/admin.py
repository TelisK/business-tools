from django.contrib import admin
from .models import Invoice, Products, Supplier

# Register your models here.
admin.site.register(Invoice)
admin.site.register(Products)
admin.site.register(Supplier)