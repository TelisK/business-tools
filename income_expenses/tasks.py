from celery import shared_task
from datetime import date, timedelta
from .models import FixedExpenses, Expenses, Store
from .views import calculate_next_charge
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

def calculate_next_charge(start_date, frequency):
    '''Calculation of next charge for fixed expenses.
    The user will enter the start date and the amount, and this function will calculate
    the next charge.
    Returns the next charge date as a date object
    '''
    if frequency == 'ANNUAL':
        next_charge = start_date + relativedelta(years=1)
    elif frequency == 'MONTHLY':
        next_charge = start_date + relativedelta(months=1)
    elif frequency == 'WEEKLY':
        next_charge = start_date + timedelta(weeks=1)
    elif frequency == 'DAILY':
        next_charge = start_date + timedelta(days=1)
    
    return next_charge

@shared_task
def generate_fixed_expenses():
    '''Adds on expenses database, each one fixed expense, depending 
    when the user selects (daily, weekly, monthly or yearly)'''

    fixed_expenses = FixedExpenses.objects.all()
    for data in fixed_expenses:
        expense_exists = Expenses.objects.filter(
            day = data.start_date,
            amount = data.amount,
            category = 'Autocreated from Fixed Expenses',
            comments = data.name + data.frequency
        ).exists()
        if not expense_exists:
            Expenses.objects.create(
            day = data.start_date,
            amount = data.amount,
            category = 'Autocreated from Fixed Expenses',
            comments = data.name + data.frequency
        )
            data.next_charge_date(data.start_date, data.frequency)


