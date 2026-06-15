from django.contrib import admin
from .models import Income, Expenses, Store, FixedExpenses

# Register your models here.
admin.site.register(Store)
admin.site.register(Income)
#admin.site.register(Expenses)
#admin.site.register(FixedExpenses)