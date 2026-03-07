from django import forms
from .models import Income, Expenses, Store

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['store', 'day', 'income_cash', 'income_pos', 'income_deposit', 
                  'income_check', 'income_other', 'comments']
        
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ['store', 'day', 'amount', 'category', 'comments']

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name']