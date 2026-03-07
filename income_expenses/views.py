from django.shortcuts import render
from income_expenses.models import Income, Expenses

# Create your views here.
def index(request):
    income_list = Income.objects.all()
    context_to_html = {'income_list':income_list}
    return render(request, 'income_expenses/index.html', context=context_to_html)

def detail(request, id):
    income_detail = Income.objects.get(id=id)
    context_to_html = {'income_detail': income_detail}
    return render (request, 'income_expenses/detail.html', context_to_html)


def totals_by_date(request, date):
    incomes = Income.objects.filter(day=date)
    expenses = Expenses.objects.filter(day=date)
    totals = incomes + expenses
    context_to_html = {'totals': totals}
    return render(request, 'income_expenses/totals_by_date.html', context_to_html)

