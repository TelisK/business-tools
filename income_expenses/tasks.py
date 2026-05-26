from celery import shared_task
from datetime import date, timedelta
from .models import FixedExpenses, Expenses, Store
from .views import calculate_next_charge

@shared_task
def generate_fixed_expenses(id):
    '''Adds on expenses database, each one fixed expense, depending 
    when the user selects (daily, weekly, monthly or yearly)'''


    pass