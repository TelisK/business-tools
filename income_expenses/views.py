from django.shortcuts import render, redirect ,get_object_or_404
from income_expenses.models import Income, Expenses, Store
from .forms import IncomeForm, ExpenseForm, StoreForm, UploadFileForm
import pandas as pd
from django.contrib import messages  # informs user with a pop up
from django.core.paginator import Paginator
from datetime import date, datetime
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import io
from .ml import prediction_model
from django.db import transaction


def income_totals_calculation(data): # Calculates the data for filtering
    totals = data.aggregate(
        total_cash = Sum('income_cash'),
        total_pos = Sum('income_pos'),
        total_deposit = Sum('income_deposit'),
        total_check = Sum('income_check'),
        total_other = Sum('income_other')                 
    )
    result = sum(v or 0 for v in totals.values())
    return totals, result

def get_totals(store,date_from,date_to):

    """ Fixing the bug with the dates on variable first_day_of_year.
    In variables income_result and expenses_result, Django accepts both types, str and date object"""
    if isinstance(date_from, str):  
        d_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    else:
        d_from = date_from

    income_result = Income.objects.filter(store=store, day__range=[date_from, date_to])
    expenses_result = Expenses.objects.filter(store=store, day__range=[date_from, date_to])

    income_totals, sum_income_result = income_totals_calculation(income_result)

    sum_expenses_result = expenses_result.aggregate(total_expenses=Sum('amount'))['total_expenses'] or 0  #The last part gives me just the number

    #d_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    first_day_of_year = d_from.replace(month=1, day=1)
    YTD_income_result = Income.objects.filter(store=store, day__range=[first_day_of_year, date_to])
    YTD_totals, YTD_result = income_totals_calculation(YTD_income_result)

    return sum_income_result, sum_expenses_result, income_totals, YTD_result, YTD_totals

def last_years_income_comparison(store, date_from, date_to):
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
    date_from = request.GET.get('date_from', today.replace(day=1))
    date_to = request.GET.get('date_to', today.replace(day=today.day -1))

    store_id = request.GET.get('store', None)

    if store_id:
        request.session['selected_store'] = store_id  # save to session
    else:
        store_id = request.session.get('selected_store', None)  # read from session

    # if not store_id:  # When user didn't use the dropdown menu, store id was not saved to the session. With this lines it's working
    #     first_store = Store.objects.filter(user=request.user).first()
    # if first_store:
    #     store_id = first_store.id
    #     request.session['selected_store'] = str(store_id)

    store = get_object_or_404(Store, id=store_id, user=request.user) if store_id else Store.objects.filter(user=request.user).first()

    sum_income_result, sum_expenses_result, income_totals, YTD_result, YTD_totals = get_totals(store,date_from,date_to)
    net_result = sum_income_result - sum_expenses_result

    income_list = Income.objects.filter(store=store).order_by('-day')
    expense_list = Expenses.objects.filter(store=store).order_by('-day')
    stores_list = Store.objects.filter(user=request.user)

    paginator_income = Paginator(income_list, 15)
    paginator_expense = Paginator(expense_list, 15)
    income_page = request.GET.get('income_page', 1)
    expense_page = request.GET.get('expense_page', 1)
    income_obj = paginator_income.get_page(income_page)
    expense_obj = paginator_expense.get_page(expense_page)

    last_year_sum_income_result, last_year_income_totals, last_year_YTD_result, last_year_YTD_totals = last_years_income_comparison(store,date_from,date_to)

    diff_by_percentage = float(f'{((sum_income_result * 100) / last_year_sum_income_result)-100:.2f}')
    diff_by_percentage_YTD = float(f'{((YTD_result * 100) / last_year_YTD_result)-100:.2f}')

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
def totals_by_date(request, date):
    store = Store.objects.filter(user=request.user).first()
    incomes = Income.objects.filter(day=date, store=store)
    expenses = Expenses.objects.filter(day=date, store=store)
    totals = incomes + expenses
    context_to_html = {'totals': totals}
    return render(request, 'income_expenses/totals_by_date.html', context=context_to_html)

@login_required
def submit_income(request):
    stores = Store.objects.filter(user=request.user)

    if request.method == 'POST':
        form = IncomeForm(request.POST)
        form.fields['store'].queryset = stores  # this filters the dropdown
        if form.is_valid():
            form.save()
            return redirect('income_expenses:index')

    else:
        form = IncomeForm()
        form.fields['store'].queryset = stores  # this filters the dropdown
        if stores.count() == 1:
            form.fields['store'].initial = stores.first() #if there's one store, the it is the default

    context_to_html = {'form':form}
    return render(request, 'income_expenses/submit_income.html', context=context_to_html)
    
@login_required
def submit_expense(request):
    stores = Store.objects.filter(user=request.user)
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
def update_income(request, id):
    stores = Store.objects.filter(user=request.user)
    income_update = Income.objects.get(id=id)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income_update)
        form.fields['store'].queryset = stores  # this filters the dropdown
        if form.is_valid():
            form.save()
            return redirect('income_expenses:detail', id=id)
    else:
        form = IncomeForm(instance=income_update)
        form.fields['store'].queryset = stores  # this filters the dropdown
        context_to_html = {'form':form}
        return render(request,'income_expenses/income_update.html', context=context_to_html)

@login_required
def update_expense(request, id):
    stores = Store.objects.filter(user=request.user)
    expense_update = Expenses.objects.get(id=id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense_update)
        form.fields['store'].queryset = stores  # this filters the dropdown
        if form.is_valid():
            form.save()
            return redirect('income_expenses:expenses_detail', id=id)
    else:
        form = ExpenseForm(instance=expense_update)
        form.fields['store'].queryset = stores  # this filters the dropdown
        context_to_html = {'form':form}
        return render(request,'income_expenses/expense_update.html', context=context_to_html)

@login_required
def delete_income(request, id):
    if request.method == 'POST':
        income_to_del = Income.objects.get(id=id)
        income_to_del.delete()
        return redirect('income_expenses:index')
    else:
        return render(request, 'income_expenses/income_delete.html')

@login_required
def delete_expense(request, id):
    if request.method == 'POST':
        expense_to_del = Expenses.objects.get(id=id)
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
            store = form.save()
            store.user.add(request.user)
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
            store_to_upd.user.add(request.user)
            return redirect('income_expenses:stores')
        else:
            return redirect('income_expenses/update_store.html')  # Needs fix because when user gives same store name as another it returns error
    else:
        form = StoreForm(instance=store_to_upd)
        context_to_html = {'form':form}
        return render(request,'income_expenses/update_store.html', context=context_to_html)

@login_required
def delete_store(request, id):
    if request.method == 'POST':
        stores = Store.objects.filter(user=request.user)
        if stores.count() == 1: # If there is one store, it cannot be deleted.
            return redirect('income_expenses:stores')
        else:
            store_to_del = get_object_or_404(Store, id=id, user=request.user)
            store_to_del.delete()
        return redirect('income_expenses:stores')
    else:
        return render(request, 'income_expenses/delete_store.html')

@login_required
def load_old_data(request): # With pandas and a predefined excel file, that user will complete, and upload it. Tha data will fill the database.
    if request.method == 'POST':
        #form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = request.FILES['file']
                df = pd.read_excel(file, parse_dates=['day'])
                df = df.dropna(subset=['day'])

                numeric_cols = ['income_cash', 'income_pos', 'income_deposit', 'income_check', 'income_other']
                df[numeric_cols] = df[numeric_cols].fillna(0)
                df['comments'] = df['comments'].fillna('')

                try:
                    with transaction.atomic(): # reads all the data if there are errors, before import to the database

                        for index, row in df.iterrows():
                            store, created = Store.objects.get_or_create(name=row['store'])
                            if created:
                                store.user.add(request.user)
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
                        
                        messages.success(request, 'Data Uploaded Successfully')
                        return redirect('income_expenses:index')
                except Exception as e:
                    # Informing the user the line of the error
                    messages.error(request, f'Σφάλμα. Ελέγξε τη γραμμή στο excel: {index + 2}: {str(e)}') 

            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, f'Errors form: {form.errors}')
        
    else:
        form = UploadFileForm()

    return render(request, 'income_expenses/load_old_data.html', {'form': form})


def export_data(request):
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





def income_expenses_analysis(request): # Analysis with matplotlib?
    pass

def prediction_with_ai(request): # with gemini api analyse the old data and based on geopolitics, bookings, how many people except to come etc.
    pass

@login_required
def prediction_with_ml(request):
    store_id = request.session.get('selected_store', None)
    store = get_object_or_404(Store, id=store_id, user=request.user)

    income_data = Income.objects.filter(store=store).values('day', 'income_cash', 'income_pos', 'income_deposit', 'income_check', 'income_other',)
    # expense_data = Expenses.objects.filter(store=store).values('day', 'amount')
    df = pd.DataFrame.from_records(income_data)
    result = prediction_model(df, days_prediction=15)
    return render(request, 'income_expenses/prediction_with_ml.html', context={'result': result})



