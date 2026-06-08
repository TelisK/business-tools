from django.contrib import admin
from .models import Invoice, Products

# Register your models here.
admin.site.register(Invoice)
admin.site.register(Products)