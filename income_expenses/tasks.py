from celery import shared_task
from datetime import date, timedelta
from .models import FixedExpenses, Expenses, Store, Income
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
from .ml import prediction_model

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
        today = date.today()

        # Using the expense_day function, gives the user the ability to add expense on the past.
        if data.next_charge_date:
            expense_day = data.next_charge_date
        else:
            expense_day = data.start_date

        while expense_day <= today: # Charges only until today.
            expense_exists = Expenses.objects.filter(
                store = data.store,
                day = expense_day,
                amount = data.amount,
                category = 'Autocreated from Fixed Expenses',
                comments = data.name + ' ' + data.frequency
            ).exists()

            if not expense_exists:
                create_expense = Expenses.objects.create(
                    store = data.store,            
                    day = expense_day,
                    amount = data.amount,
                    category = 'Autocreated from Fixed Expenses',
                    comments = data.name + ' ' + data.frequency
                )
            expense_day = calculate_next_charge(expense_day, data.frequency)

                
        data.save()


@shared_task
def store_predicted_income():
    '''Adds every day the prediction of machine learning model
    to the database. This way we can train our model with the prediction
    error and make it better.'''

    stores = Store.objects.all()

    for store in stores:
        income_data = Income.objects.filter(store=store).values(
            'day', 'income_cash', 'income_pos', 'income_deposit', 'income_check', 'income_other',
        )
        if not income_data.exists():
            continue

        else:
            try:
                df = pd.DataFrame.from_records(income_data)
                tomorrows_prediction = prediction_model(df, days_prediction=1)

                add_prediction = Income.objects.create(
                    store = store,
                    day = tomorrows_prediction[0]['day'],
                    income_cash=0,
                    income_pos=0,
                    income_deposit=0,
                    income_check=0,
                    income_other=0,
                    predicted_income = tomorrows_prediction[0]['predicted_income']
                )
            
            except Exception as e:
                print(e)
                continue


        


