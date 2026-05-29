from celery import shared_task
from datetime import date, timedelta
from .models import FixedExpenses, Expenses, Store
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
    print(f"Found {fixed_expenses.count()} fixed expenses")
    for data in fixed_expenses:
        print(f"Processing: {data.name}")
        print(f"start_date: {data.start_date}")
        print(f"next_charge_date: {data.next_charge_date}")
        print(f"is_active: {data.is_active}")

        today = date.today()

        # Using the expense_day function, gives the user the ability to add expense on the past.
        if data.next_charge_date:
            expense_day = data.next_charge_date
        else:
            expense_day = data.start_date
        print(f"expense_day: {expense_day}, today: {today}")

        while expense_day <= today: # Charges only until today.
            print(f"Entering while loop: {expense_day} <= {today}")
            expense_exists = Expenses.objects.filter(
                store = data.store,
                day = expense_day,
                amount = data.amount,
                category = 'Autocreated from Fixed Expenses',
                comments = data.name + ' ' + data.frequency
            ).exists()
            print(f"Expense exists: {expense_exists}")
            if not expense_exists:
                print(f"Creating expense for {expense_day}")
                create_expense = Expenses.objects.create(
                    store = data.store,            
                    day = expense_day,
                    amount = data.amount,
                    category = 'Autocreated from Fixed Expenses',
                    comments = data.name + ' ' + data.frequency
                )
            expense_day = calculate_next_charge(expense_day, data.frequency)
            print(f"Updated expense_day to: {expense_day}")
                
        data.save()


