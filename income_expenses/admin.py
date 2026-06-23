from django.contrib import admin
from .models import Income, Expenses, Store, FixedExpenses, AI_Usage, AI_Limit

# Register your models here.
admin.site.register(Store)
#admin.site.register(Income)
#admin.site.register(Expenses)
#admin.site.register(FixedExpenses)
admin.site.register(AI_Limit)
admin.site.register(AI_Usage)