from django import forms
from .models import Income, Expenses, Store

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['store', 'day', 'income_cash', 'income_pos', 'income_deposit', 
                  'income_check', 'income_other', 'comments']
        widgets = {
            'day': forms.DateInput(attrs={'type':'date'}, format='%Y-%m-%d'), # Displays a calendar
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ['store', 'day', 'amount', 'category', 'comments']
        widgets = {
            'day': forms.DateInput(attrs={'type':'date'}, format='%Y-%m-%d' ), # Displays a calendar
        }

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name']

class UploadFileForm(forms.Form):
    file = forms.FileField()