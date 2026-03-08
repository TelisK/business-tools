from django.shortcuts import render, redirect
from income_expenses.models import Income, Expenses, Store
from django.shortcuts import get_object_or_404
from .forms import IncomeForm, ExpenseForm, StoreForm


# Create your views here.
def index(request):
    income_list = Income.objects.all()
    expense_list = Expenses.objects.all()
    context_to_html = {'income_list':income_list, 'expense_list':expense_list}
    return render(request, 'income_expenses/index.html', context=context_to_html)

def detail(request, id):
    income_detail = get_object_or_404(Income, id=id)
    context_to_html = {'income_detail': income_detail}
    return render (request, 'income_expenses/detail.html', context=context_to_html)

def expenses_detail(request,id):
    expense_detail = get_object_or_404(Expenses, id=id)
    context_to_html = {'expense_detail': expense_detail}
    return render(request, 'income_expenses/expenses_detail.html', context=context_to_html)

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
        context_to_html = {'form':form}
        return render(request, 'income_expenses/submit_income.html', context=context_to_html)
    

def submit_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.isvalid():
            form.save()
            return redirect('income_expenses:index')
    
    else:
        form = ExpenseForm()
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
        store_to_del = Store.objects.get(id=id)
        store_to_del.delete()
        return redirect('income_expenses:stores')
    else:
        return render(request, 'income_expenses/delete_store.html')
