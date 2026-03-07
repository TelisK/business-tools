from django.shortcuts import render, redirect
from income_expenses.models import Income, Expenses
from django.shortcuts import get_object_or_404
from .forms import IncomeForm, ExpenseForm, StoreForm


# Create your views here.
def index(request):
    income_list = Income.objects.all()
    context_to_html = {'income_list':income_list}
    return render(request, 'income_expenses/index.html', context=context_to_html)

def detail(request, id):
    income_detail = get_object_or_404(Income, id=id)
    context_to_html = {'income_detail': income_detail}
    return render (request, 'income_expenses/detail.html', context=context_to_html)


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