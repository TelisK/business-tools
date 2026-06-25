from django.shortcuts import render, redirect ,get_object_or_404
from income_expenses.models import Income, Expenses, Store, FixedExpenses
from .forms import IncomeForm, ExpenseForm, StoreForm, UploadFileForm, FixedExpenseForm
import pandas as pd
from django.contrib import messages  # informs user with a pop up
from django.core.paginator import Paginator
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import io
from .ml import prediction_model
from django.db import transaction
import plotly.express as px
from django.conf import settings
from decimal import Decimal



def income_totals_calculation(data):
    """
    Calculates the data for filtering.
    Makes the addition and returns a dictionary."""
    # totals will become a dictionary
    totals = data.aggregate(
        total_cash = Sum('income_cash'),
        total_pos = Sum('income_pos'),
        total_deposit = Sum('income_deposit'),
        total_check = Sum('income_check'),
        total_other = Sum('income_other')
    )
    # replace None with 0
    totals = {key : (value or 0) for key, value in totals.items()}

    result = sum(v or 0 for v in totals.values())
    return totals, result

def get_totals(store,date_from,date_to):

    """ Fixing the bug with the dates on variable first_day_of_year.
    In variables income_result and expenses_result, Django accepts both types, str and date object"""
    if isinstance(date_from, str):  
        d_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    else:
        d_from = date_from

    income_result = Income.objects.filter(store=store, day__range=[date_from, date_to]).order_by('day')
    expenses_result = Expenses.objects.filter(store=store, day__range=[date_from, date_to]).order_by('day')
    expenses_fpa = Expenses.objects.filter(
        store=store, day__range=[date_from, date_to], category='WITH_FPA_TAX'
    ).order_by('day')

    expenses_fpa = expenses_fpa.aggregate(total_expenses=Sum('amount'))['total_expenses'] or 0

    income_df = pd.DataFrame.from_records(income_result.values(
        'day', 'income_cash', 'income_pos', 'income_deposit', 'income_check', 'income_other'
    ))
    expenses_df = pd.DataFrame.from_records(expenses_result.values(
        'day', 'amount'
    ))

    income_totals, sum_income_result = income_totals_calculation(income_result)

    sum_expenses_result = expenses_result.aggregate(total_expenses=Sum('amount'))['total_expenses'] or 0  
    #The last part gives me just the number

    #d_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    first_day_of_year = d_from.replace(month=1, day=1)
    YTD_income_result = Income.objects.filter(store=store, day__range=[first_day_of_year, date_to])
    YTD_totals, YTD_result = income_totals_calculation(YTD_income_result)

    return sum_income_result, sum_expenses_result, expenses_fpa, income_totals, YTD_result, YTD_totals, \
    income_df, expenses_df, income_result, expenses_result

def last_years_income_comparison(store, date_from, date_to):
    """
    Picks the dates and calculates the amount of last year, same dates.
    We can compare last years income with todays income and give the user
    a percentage of growing or decreasing."""
    if isinstance(date_from, str):
        d_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    else:
        d_from = date_from

    if isinstance(date_to, str):
        d_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    else:
        d_to = date_to


    last_year_date_from = d_from.replace(year=d_from.year - 1)
    last_year_date_to = d_to.replace(year=d_to.year - 1)
    last_year_first_day = d_from.replace(year=d_from.year - 1, month=1, day=1)

    last_year_result = Income.objects.filter(store=store, day__range=[last_year_date_from, last_year_date_to])
    last_year_income_totals, last_year_sum_income_result = income_totals_calculation(last_year_result)

    last_year_result_YTD = Income.objects.filter(store=store, day__range=[last_year_first_day, last_year_date_to])
    last_year_YTD_totals, last_year_YTD_result = income_totals_calculation(last_year_result_YTD)


    return last_year_sum_income_result, last_year_income_totals, last_year_YTD_result, last_year_YTD_totals


# Create your views here.
@login_required
def index(request):
    today = date.today()
    yesterday = today - timedelta(days=1)
    date_from = request.GET.get('date_from', today.replace(day=1))
    # Using the previous day of today because the income submit is at the end of the day. 
    # This way we have correct percentage.
    date_to = request.GET.get('date_to', yesterday)

    user_store = Store.objects.filter(user=request.user)
    if not user_store.exists():
        messages.error(request, 'User has no stores')
        return redirect('income_expenses:stores')

    store_id = request.GET.get('store')
    if user_store.filter(id=store_id).exists():
        request.session['selected_store'] = store_id  # save to session
    else:
        store_id = None

    if not store_id:
        store_id = request.session.get('selected_store')
    
    if not store_id:
        store_id = user_store.first().id # pick up the first one from the database
        request.session['selected_store'] = store_id  # save to session


    store = get_object_or_404(Store, id=store_id, user=request.user) \
          if store_id else Store.objects.filter(user=request.user).first()

    sum_income_result, sum_expenses_result, expenses_fpa, income_totals, YTD_result, YTD_totals, \
        income_df, expenses_df, income_result, expenses_result= \
        get_totals(store,date_from,date_to)
    
    net_result = sum_income_result - sum_expenses_result

    income_list = Income.objects.filter(store=store).order_by('-day')
    #print(income_list[:10])
    expense_list = Expenses.objects.filter(store=store).order_by('-day')
    stores_list = Store.objects.filter(user=request.user)

    # paginator_income = Paginator(income_list, 15)
    # paginator_expense = Paginator(expense_list, 15)
    # income_page = request.GET.get('income_page', 1)
    # expense_page = request.GET.get('expense_page', 1)
    # income_obj = paginator_income.get_page(income_page)
    # expense_obj = paginator_expense.get_page(expense_page)
    income_obj = income_list[:10]
    expense_obj = expense_list[:10]

    last_year_sum_income_result, last_year_income_totals, last_year_YTD_result, last_year_YTD_totals = \
        last_years_income_comparison(store,date_from,date_to)

    if last_year_sum_income_result != 0:
        diff_by_percentage = float(f'{((sum_income_result * 100) / last_year_sum_income_result)-100:.2f}')
    else:
        diff_by_percentage = '-'
    if last_year_YTD_result !=0:
        diff_by_percentage_YTD = float(f'{((YTD_result * 100) / last_year_YTD_result)-100:.2f}')
    else:
        diff_by_percentage_YTD = '-'

    context_to_html = {
        'store':store,
        'stores_list':stores_list,
        'sum_income_result':sum_income_result,
        'sum_expenses_result':sum_expenses_result,
        'income_totals':income_totals,
        'net_result':net_result,
        'date_from':date_from,
        'date_to':date_to,
        'income_list':income_obj,
        'expense_list':expense_obj,
        'YTD_result':YTD_result,
        'diff_by_percentage':diff_by_percentage,
        'diff_by_percentage_YTD':diff_by_percentage_YTD

    }
    return render(request, 'income_expenses/index.html', context=context_to_html)

@login_required
def detail(request, id):
    income_detail = get_object_or_404(Income, id=id, store__user=request.user) # double underscore lookup, for relationship
    context_to_html = {'income_detail': income_detail}
    return render (request, 'income_expenses/detail.html', context=context_to_html)

@login_required
def expenses_detail(request,id):
    expense_detail = get_object_or_404(Expenses, id=id, store__user=request.user)
    context_to_html = {'expense_detail': expense_detail}
    return render(request, 'income_expenses/expenses_detail.html', context=context_to_html)


# needs completion
@login_required
def analytics(request):
    '''
    The user will choose the dates he wants, and the application will return the income and expenses data.
    Also will have some graphs and comparison with different time.
    The default dates are from 1st of January until today.
    '''
    today = date.today()
    first_day_of_the_year = today.replace(day=1, month=1)

    store = Store.objects.filter(user=request.user)
    store_id = request.session.get('selected_store')

    start_date = request.GET.get('start_date', first_day_of_the_year)
    end_date = request.GET.get('end_date', today)
    
    sum_income_result, sum_expenses_result, expenses_fpa, income_totals, YTD_result, YTD_totals, \
         income_df, expenses_df, income_result, expenses_result = get_totals(
        store_id, start_date, end_date
    )
    # tax removal to calculate net result
    net_income = sum_income_result/Decimal(1.24)
    fpa_income_tax = sum_income_result - net_income
    net_expenses = expenses_fpa/Decimal(1.24)
    fpa_expenses_tax = expenses_fpa - net_expenses

    if net_income != 0:
        gross_profit_margin = ((net_income - net_expenses)/net_income)*100 # Περιθώριο Μικτού Κέρδους
    else:
        gross_profit_margin = 0
    # break_even_point =     # (νεκρό σημείο) have to calculate the fixed expenses


    # I am changing the value of net expenses. I added all the expenses, including with fpa tax and no fpa tax, and I
    # substracted the expenses with fpa tax.
    net_expenses += sum_expenses_result - expenses_fpa

    net_result = net_income - net_expenses

    if net_income != 0:
        net_profit_margin = (net_result / net_income)*100 # Περιθώριο Καθαρού Κέρδους
    else:
        net_profit_margin = 0
    
    if income_df.empty: # if we have no expenses, it creates the dataframe empty.
        income_df = pd.DataFrame(columns=['day', 'income_cash', 'income_pos', 'income_deposit', 'income_check', 'income_other'])

    income_df['total_income'] = income_df[[
        'income_cash', 'income_pos', 'income_deposit', 'income_check', 'income_other'
    ]].sum(axis=1)

    income_max = income_df['total_income'].max()
    income_average = income_df['total_income'].mean()

    income_df['net_income'] = income_df['total_income'].div(Decimal(1.24))
    income_df['fpa_tax'] = income_df['total_income'] - income_df['net_income']

    income_df = income_df.rename(columns={
    'total_income':'Συνολικό_Εισόδημα',
    'income_cash': 'Μετρητά',
    'income_pos': 'POS',
    'income_deposit': 'Κατάθεση',
    'income_check': 'Επιταγή',
    'income_other': 'Άλλο',
    'net_income': 'Καθαρό Εισόδημα',
    'fpa_tax': 'ΦΠΑ'
})

    # making all dates to datetime.date
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    fig = px.line(
        income_df, 
        x='day', 
        y='Καθαρό Εισόδημα', 
        title=f'Εισοδήματα απο {start_date.strftime('%d/%m/%Y')} έως {end_date.strftime('%d/%m/%Y')}',
        labels={'day':'Ημερομηνία', 'Καθαρό Εισόδημα':'Καθαρό Εισόδημα πρό φόρων σε €'}
    )

    chart = fig.to_html(include_plotlyjs='cdn')


    
    fig2 = px.line(
        income_df,
        x='day',
        y=['Μετρητά', 'POS', 'Κατάθεση', 'Επιταγή', 'Άλλο'],
        title=f'Αναλυτικά απο {start_date.strftime('%d/%m/%Y')} έως {end_date.strftime('%d/%m/%Y')}',
        labels={'day':'Ημερομηνία', 'value':'Τζίρος σε €'}
    )

    chart2 = fig2.to_html(include_plotlyjs='cdn')

    if expenses_df.empty: # if we have no expenses, it creates the dataframe empty.
        expenses_df = pd.DataFrame(columns=['day', 'Συνολικά_Έξοδα'])
    else:
        expenses_df = expenses_df.groupby('day')['amount'].sum().reset_index() # adds same day's expenses in one.
        expenses_df.rename(columns={'amount': 'Συνολικά_Έξοδα'}, inplace=True)

    df = income_df.merge(expenses_df, on='day', how='outer').fillna(0) # outer shows all days (if expense or income not exists)

    fig3 = px.line(
        df,
        x='day',
        y=['Συνολικό_Εισόδημα', 'Συνολικά_Έξοδα'],
        title=f'Έσοδα - Έξοδα απο {start_date.strftime('%d/%m/%Y')} έως {end_date.strftime('%d/%m/%Y')} συμπεριλαμβάνουν ΦΠΑ',
        labels={'day':'Ημερομηνία', 'value':'Έσοδα - Έξοδα σε €'}
    )

    chart3 = fig3.to_html(include_plotlyjs='cdn')

    if not income_df.empty:

        income_sum_for_pie = {
            'Μετρητά':income_df['Μετρητά'].sum(),
            'POS':income_df['POS'].sum(),
            'Κατάθεση':income_df['Κατάθεση'].sum(),
            'Επιταγή':income_df['Επιταγή'].sum(),
            'Άλλο':income_df['Άλλο'].sum(),
        }

        # Removes values when they are zeros. So on the pie will not be visible ways of payment with 0 income
        income_sum_for_pie = {key: value for key, value in income_sum_for_pie.items() if value > 0}

        fig4 = px.pie(names=list(income_sum_for_pie.keys()),
                    values=list(income_sum_for_pie.values()),
                    title=f'Ποσοστό χρήσης τρόπων πληρωμής απο {start_date.strftime('%d/%m/%Y')} έως {end_date.strftime('%d/%m/%Y')}')

        chart4 = fig4.to_html(include_plotlyjs='cdn')

    else:
        chart4 = None

    if not income_df.empty:
        days_dict = {0:'Κυριακή',1:'Δευτέρα', 2:'Τρίτη',3:'Τετάρτη',4:'Πέμπτη',5:'Παρασκευή',6:'Σάββατο'}
        days_list = []
        for income_date in income_df['day']:
            real_day = income_date.weekday()
            days_list.append(days_dict[real_day])

        income_df['day_name'] = days_list # cannot add values on df inside the loop! 


        income_day_for_pie = income_df.groupby('day_name')['Συνολικό_Εισόδημα'].sum().to_dict()

        fig5 = px.pie(names = list(income_day_for_pie.keys()),
                      values = list(income_day_for_pie.values()),
                      title=f'Ποσοστό εισπράξεων ανα ημέρα απο {start_date.strftime('%d/%m/%Y')} έως {end_date.strftime('%d/%m/%Y')}')
        

        chart5 = fig5.to_html(include_plotlyjs='cdn')
    else:
        chart5 = None

    # Display the dataframe on the html
    # income_df_html = income_df.to_html(classes='table table-striped')


    

    context_to_html = {
        'sum_income_result' : sum_income_result,
        'sum_expenses_result' : sum_expenses_result,
        'income_totals':income_totals,
        'net_result' : net_result,
        'YTD_result' : YTD_result,
        'YTD_totals' : YTD_totals,
        'chart' : chart,
        'chart2' : chart2,
        'chart3' : chart3,
        'chart4' : chart4,
        'chart5' : chart5,
        #'income_df_html' : income_df_html,
        'income_result' : income_result,
        'expenses_result' : expenses_result,
        'income_max' : income_max,
        'income_average' : income_average,
        'fpa_income_tax' : fpa_income_tax,
        'fpa_expenses_tax' : fpa_expenses_tax,
        'gross_profit_margin' : gross_profit_margin,
        'net_profit_margin' : net_profit_margin,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'income_expenses/analytics.html', context=context_to_html)

@login_required
def submit_income(request):
    store_id = request.session.get('selected_store')
    stores = Store.objects.filter(user=request.user, id=store_id)

    if request.method == 'POST':
        form = IncomeForm(request.POST)
        form.fields['store'].queryset = stores  # this filters the dropdown
        if form.is_valid():
            form.save()
            return redirect('income_expenses:index')
        else:
            messages.error(request, 'H Ημερομηνία είναι καταχωρημένη ήδη.')

    else:
        form = IncomeForm()
        form.fields['store'].queryset = stores  # this filters the dropdown
        if stores.count() == 1:
            form.fields['store'].initial = stores.first() #if there's one store, the it is the default

    context_to_html = {'form':form}
    return render(request, 'income_expenses/submit_income.html', context=context_to_html)
    
@login_required
def submit_expense(request):
    store_id = request.session.get('selected_store')
    stores = Store.objects.filter(user=request.user, id=store_id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        form.fields['store'].queryset = stores  # this filters the dropdown
        if form.is_valid():
            form.save()
            return redirect('income_expenses:index')
    
    else:
        form = ExpenseForm()
        form.fields['store'].queryset = stores  # this filters the dropdown
        if stores.count() == 1:
            form.fields['store'].initial = stores.first() #if there's one store, the it is the default
    context_to_html = {'form':form}
    return render(request, 'income_expenses/submit_expense.html', context=context_to_html)

@login_required
def fixed_expenses(request):
    store_id = request.session.get('selected_store')
    store = get_object_or_404(Store, id=store_id, user=request.user)
    fixed_expenses_list = FixedExpenses.objects.filter(store=store)
    if request.method == 'POST':
        form = FixedExpenseForm(request.POST)
        form.fields['store'].queryset = Store.objects.filter(user=request.user) #filters dropdown

        if form.is_valid():
            fixed_expense = form.save(commit=False)
            fixed_expense.save()
            return redirect('income_expenses:fixed_expenses')
        else:
            messages.error(request, 'Ελέγξε τη φόρμα')
            return render(request, 'income_expenses/fixed_expenses.html', {'form':form})

    else:
        form = FixedExpenseForm()
        form.fields['store'].queryset = Store.objects.filter(user=request.user)

    context_to_html = {'fixed_expenses_list':fixed_expenses_list, 'form':form}
    return render(request, 'income_expenses/fixed_expenses.html', context=context_to_html)

@login_required
def delete_fixed_expense(request, id):
    fixed_expense = get_object_or_404(FixedExpenses, id=id, store__user=request.user)
    if request.method == 'POST':
        fixed_expense.delete()
        return redirect('income_expenses:fixed_expenses')
    else:
        return render(request,'income_expenses/delete_fixed_expense.html')


@login_required
def update_income(request, id):
    stores = Store.objects.filter(user=request.user)
    income_update = get_object_or_404(Income, id=id, store__user=request.user)
    
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income_update)
        form.fields['store'].queryset = stores  # this filters the dropdown
        if form.is_valid():
            form.save()
            if next_url:
                return redirect(next_url)
            return redirect('income_expenses:detail', id=id)
        else:
            messages.error(request, 'Ελέγξε τη φόρμα')
            return render(request, 'income_expenses/income_update.html', {'form':form})
    else:
        form = IncomeForm(instance=income_update)
        form.fields['store'].queryset = stores  # this filters the dropdown
        context_to_html = {'form':form}
        return render(request,'income_expenses/income_update.html', context=context_to_html)

@login_required
def update_expense(request, id):
    stores = Store.objects.filter(user=request.user)
    expense_update = get_object_or_404(Expenses, id=id, store__user=request.user)
    # redirects to the page the user entered on the update. We check below if next_url ...
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense_update)
        form.fields['store'].queryset = stores  # this filters the dropdown
        if form.is_valid():
            form.save()
            if next_url:
                return redirect(next_url)
            return redirect('income_expenses:expenses_detail', id=id)
        else:
            messages.error(request, 'Έλεγξε τη φόρμα')
            return render(request, 'income_expenses/expense_update.html', {'form':form})
    else:
        form = ExpenseForm(instance=expense_update)
        form.fields['store'].queryset = stores  # this filters the dropdown
        context_to_html = {'form':form}
        return render(request,'income_expenses/expense_update.html', context=context_to_html)

@login_required
def delete_income(request, id):
    income_to_del = get_object_or_404(Income, id=id, store__user=request.user)
    if request.method == 'POST':
        income_to_del.delete()
        return redirect('income_expenses:index')
    else:
        return render(request, 'income_expenses/income_delete.html')

@login_required
def delete_expense(request, id):
    expense_to_del = get_object_or_404(Expenses, id=id, store__user=request.user)
    if request.method == 'POST':
        expense_to_del.delete()
        return redirect('income_expenses:index')
    else:
        return render(request, 'income_expenses/expense_delete.html')
    
@login_required
def stores(request):
    stores_list = Store.objects.filter(user=request.user)
    context_to_html = {'stores_list': stores_list}
    return render(request, 'income_expenses/stores.html', context=context_to_html)

@login_required
def add_store(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save(commit=False)
            store.user = request.user
            store.save()
            return redirect('income_expenses:index')
    else:
        form = StoreForm()
        
    context_to_html = {'form':form}
    return render(request, 'income_expenses/add_store.html', context=context_to_html)
    
@login_required
def update_store(request, id):
    store_to_upd = get_object_or_404(Store, id=id, user=request.user)
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store_to_upd)
        if form.is_valid():
            form.save()
            #store_to_upd.user.add(request.user)
            return redirect('income_expenses:stores')
        else:
            return redirect('income_expenses/update_store.html')
    else:
        form = StoreForm(instance=store_to_upd)
        context_to_html = {'form':form}
        return render(request,'income_expenses/update_store.html', context=context_to_html)

@login_required
def delete_store(request, id):
    """User cannot delete the last store. This is for data protection."""
    if request.method == 'POST':
        store_to_del = get_object_or_404(Store, id=id, user=request.user)
        stores = Store.objects.filter(user=request.user)
        if stores.count() == 1: # If there is one store, it cannot be deleted.
            return redirect('income_expenses:stores')
        
        store_to_del.delete()
        return redirect('income_expenses:stores')
    else:
        return render(request, 'income_expenses/delete_store.html')

@login_required
# With pandas and a predefined excel file, that user will complete, and upload it. Tha data will fill the database.
def load_old_data(request): 
    """
    User can download the excel file, fill the dates with the data, and upload it
    to the program.
    User must keep the columns name as they are, because pandas reads and categorize 
    the data on the database.
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = request.FILES['file']
                # convert the 'day' column from Excel to Python datetime
                df = pd.read_excel(file, parse_dates=['day'], sheet_name='Έσοδα')
                df = df.dropna(subset=['day']) # Drops data if day is missing

                numeric_cols = ['income_cash', 'income_pos', 'income_deposit', 'income_check', 'income_other']
                df[numeric_cols] = df[numeric_cols].fillna(0)
                df['comments'] = df['comments'].fillna('')

                df_expenses = pd.read_excel(file, parse_dates=['day'], sheet_name='Έξοδα')
                df_expenses = df_expenses.dropna(subset=['day'])

                numeric_cols_expenses = ['amount']
                df_expenses[numeric_cols_expenses] = df_expenses[numeric_cols_expenses].fillna(0)
                df_expenses['comments'] = df_expenses['comments'].fillna('')
                df_expenses['category'] = df_expenses['category'].fillna('')

                try:
                    with transaction.atomic(): # reads all the data if there are errors, before import to the database
                        
                        try:
                            for index, row in df.iterrows():
                                store, created = Store.objects.get_or_create(name=row['store'], user=request.user)

                                Income.objects.create(
                                    store = store,
                                    day = row['day'],
                                    income_cash = row['income_cash'],
                                    income_pos = row['income_pos'],
                                    income_deposit = row['income_deposit'],
                                    income_check = row['income_check'],
                                    income_other = row['income_other'],
                                    comments = row['comments']
                                )

                        except Exception as e:
                            # Informing the user the line of the error
                            messages.error(request, f'Σφάλμα. Ελέγξε τη γραμμή στο φύλλο Έσοδα: {index + 2}: {str(e)}')
                            raise # If there is an error on first loop, it stops here. 
                                    # We don't want to go to the second for loop.                       

                        try:

                            for index, row in df_expenses.iterrows():
                                store, created = Store.objects.get_or_create(name=row['store'], defaults={'user':request.user})

                                Expenses.objects.create(
                                    store = store,
                                    day = row['day'],
                                    amount = row['amount'],
                                    category = row['category'],
                                    comments = row['comments']
                                )

                            messages.success(request, 'Data Uploaded Successfully')

                            return redirect('income_expenses:index')

                        except Exception as e:
                            # Informing the user the line of the error
                            messages.error(request, f'Σφάλμα. Ελέγξε τη γραμμή στο φύλλο Έξοδα: {index + 2}: {str(e)}')
                            raise # If the error is in the second loop, it stops here. We don't want to see more erros!

                except Exception as e:
                    messages.error(request, f'Error: {str(e)}')
            except Exception as e:
                    messages.error(request, f'Error: {str(e)}')
            
        else:
            messages.error(request, f'Errors form: {form.errors}')
        
    else:
        form = UploadFileForm()

    return render(request, 'income_expenses/load_old_data.html', {'form': form})


def export_data(request):
    """
    Gets income and expenses data from the database and creates an excel file
    with two sheets, one for income, and one for expenses.
    """
    store_id = request.session.get('selected_store', None)
    store_to_export = get_object_or_404(Store, id=store_id, user=request.user)
    income_list = Income.objects.filter(store=store_to_export)
    expenses_list = Expenses.objects.filter(store=store_to_export)
    income_values = income_list.values('store','day','income_cash','income_pos','income_deposit','income_check',
                                       'income_other','comments')
    expenses_values = expenses_list.values('store','day','amount','category','comments')
    df_income = pd.DataFrame.from_records(income_values)
    df_expenses = pd.DataFrame.from_records(expenses_values)
    
    #We need buffer to save the file to the users computer, not to the server.
    buffer = io.BytesIO()  # create empty virtual file
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:   # write excel data into it
        df_income.to_excel(writer, sheet_name='Έσοδα', index=False)
        df_expenses.to_excel(writer, sheet_name='Έξοδα', index=False) 

    buffer.seek(0)         # go back to the beginning


    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=export.xlsx'
    return response


def prediction_with_ai(request): 
    '''with gemini api analyse the old data and based on geopolitics, 
    bookings, how many people except to come etc.'''
    pass

@login_required
def prediction_with_ml(request):
    """
    Gets all income data from the database, feeds the prediction model and
    takes a 15 days prediction, with the income sum of each day.
    """
    store_id = request.session.get('selected_store', None)
    store = get_object_or_404(Store, id=store_id, user=request.user)

    income_data = Income.objects.filter(store=store).values(
        'day', 'income_cash', 'income_pos', 'income_deposit', 'income_check', 'income_other',
    )
    if not income_data:
        messages.error(request, 'There are no data to make predictions!')
        return redirect('income_expenses:index')
    # expense_data = Expenses.objects.filter(store=store).values('day', 'amount')
    df = pd.DataFrame.from_records(income_data)
    result = prediction_model(df, days_prediction=15)
    return render(request, 'income_expenses/prediction_with_ml.html', context={'result': result})


def privacy_policy(request):
    return render(request, 'income_expenses/privacy_policy.html', {'contact_email': settings.CONTACT_EMAIL})
