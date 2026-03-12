from django.shortcuts import render, redirect ,get_object_or_404
from income_expenses.models import Income, Expenses, Store
from .forms import IncomeForm, ExpenseForm, StoreForm, UploadFileForm
import pandas as pd
from django.contrib import messages  # informs user with a pop up
from django.core.paginator import Paginator
from datetime import date
from django.db.models import Sum


# Create your views here.
def index(request):
    income_list = Income.objects.all()
    expense_list = Expenses.objects.all()

    paginator_income = Paginator(income_list, 25)
    paginator_expense = Paginator(expense_list, 25)
    income_page = request.GET.get('income_page', 1)
    expense_page = request.GET.get('expense_page', 1)
    income_obj = paginator_income.get_page(income_page)
    expense_obj = paginator_expense.get_page(expense_page)

    context_to_html = {'income_list':income_obj, 'expense_list':expense_obj}
    return render(request, 'income_expenses/index.html', context=context_to_html)

def detail(request, id):
    income_detail = get_object_or_404(Income, id=id)
    context_to_html = {'income_detail': income_detail}
    return render (request, 'income_expenses/detail.html', context=context_to_html)

def expenses_detail(request,id):
    expense_detail = get_object_or_404(Expenses, id=id)
    context_to_html = {'expense_detail': expense_detail}
    return render(request, 'income_expenses/expenses_detail.html', context=context_to_html)

def summary_and_statistics(request):
    #default page
    today = date.today()
    date_from = request.GET.get('date_from', today.replace(day=1))
    date_to = request.GET.get('date_to', today)

    income_result = Income.objects.filter(date__range=[date_from, date_to])
    expenses_result = Expenses.objects.filter(date__range=[date_from, date_to])

    fields_to_sum = ['income_cash', 'income_pos', 'income_deposit', 'income_check', 'income_other']
    sum_income_result = Income.objects.aggregate(Sum(income_result[fields_to_sum]))
    sum_expenses_result = Expenses.objects.aggregate(Sum(expenses_result[fields_to_sum]))

# needs completion
def totals_by_date(request, date):
    incomes = Income.objects.filter(day=date)
    expenses = Expenses.objects.filter(day=date)
    totals = incomes + expenses
    context_to_html = {'totals': totals}
    return render(request, 'income_expenses/totals_by_date.html', context=context_to_html)

def submit_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('income_expenses:index')

    else:
        form = IncomeForm()
        stores = Store.objects.all()
        if stores.count() == 1:
            form.fields['store'].initial = stores.first() #if there's one store, the it is the default
        context_to_html = {'form':form}
        return render(request, 'income_expenses/submit_income.html', context=context_to_html)
    

def submit_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('income_expenses:index')
    
    else:
        form = ExpenseForm()
        stores = Store.objects.all()
        if stores.count() == 1:
            form.fields['store'].initial = stores.first() #if there's one store, the it is the default
        context_to_html = {'form':form}
        return render(request, 'income_expenses/submit_expense.html', context=context_to_html)
    
def update_income(request, id):
    income_update = Income.objects.get(id=id)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income_update)
        if form.is_valid():
            form.save()
            return redirect('income_expenses:detail', id=id)
    else:
        form = IncomeForm(instance=income_update)
        context_to_html = {'form':form}
        return render(request,'income_expenses/income_update.html', context=context_to_html)

def update_expense(request, id):
    expense_update = Expenses.objects.get(id=id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense_update)
        if form.is_valid():
            form.save()
            return redirect('income_expenses:expenses_detail', id=id)
    else:
        form = ExpenseForm(instance=expense_update)
        context_to_html = {'form':form}
        return render(request,'income_expenses/expense_update.html', context=context_to_html)

def delete_income(request, id):
    if request.method == 'POST':
        income_to_del = Income.objects.get(id=id)
        income_to_del.delete()
        return redirect('income_expenses:index')
    else:
        return render(request, 'income_expenses/income_delete.html')


def delete_expense(request, id):
    if request.method == 'POST':
        expense_to_del = Expenses.objects.get(id=id)
        expense_to_del.delete()
        return redirect('income_expenses:index')
    else:
        return render(request, 'income_expenses/expense_delete.html')
    
def stores(request):
    stores_list = Store.objects.all()
    context_to_html = {'stores_list': stores_list}
    return render(request, 'income_expenses/stores.html', context=context_to_html)

def add_store(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('income_expenses:index')
        
    else:
        form = StoreForm()
        context_to_html = {'form':form}
        return render(request, 'income_expenses/add_store.html', context=context_to_html)
    
def update_store(request, id):
    update_store = Store.objects.get(id=id)
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=update_store)
        if form.is_valid():
            form.save()
            return redirect('income_expenses:stores')
    else:
        form = StoreForm(instance=update_store)
        context_to_html = {'form':form}
        return render(request,'income_expenses/update_store.html', context=context_to_html)


def delete_store(request, id):
    if request.method == 'POST':
        stores = Store.objects.all()
        if stores.count() == 1: # If there is one store, it cannot be deleted.
            return redirect('income_expenses:stores')
        else:
            store_to_del = Store.objects.get(id=id)
            store_to_del.delete()
        return redirect('income_expenses:stores')
    else:
        return render(request, 'income_expenses/delete_store.html')

def load_old_data(request): # With pandas and a predefined excel file, that user will complete, and upload it. Tha data will fill the database.
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = request.FILES['file']
                df = pd.read_excel(file)

                numeric_cols = ['income_cash', 'income_pos', 'income_deposit', 'income_check', 'income_other']
                df[numeric_cols] = df[numeric_cols].fillna(0)
                df['comments'] = df['comments'].fillna('')

                for index, row in df.iterrows():
                    store, created = Store.objects.get_or_create(name=row['store'])
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
                messages.error(request, f'Σφάλμα: {str(e)}')
        else:
            messages.error(request, f'Σφάλματα form: {form.errors}')
        
    else:
        form = UploadFileForm()

    return render(request, 'income_expenses/load_old_data.html', {'form': form})



def income_expenses_analysis(request): # Analysis with matplotlib?
    pass

def prediction_with_ai(request): # with gemini api analyse the old data and based on geopolitics, bookings, how many people except to come etc.
    pass

def prediction_with_ml(request):
    pass

