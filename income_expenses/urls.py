from django.urls import path
from . import views

app_name = 'income_expenses'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:id>/', views.detail, name='detail'),
    path('expenses/<int:id>/', views.expenses_detail, name= 'expenses_detail'),
    path('add_income/', views.submit_income, name='submit_income'),
    path('add_expense/', views.submit_expense, name='submit_expense'),
    path('add_store/', views.add_store, name='add_store'),
    path('income_delete/<int:id>/', views.delete_income, name='income_delete'),
    path('expense_delete/<int:id>/', views.delete_expense, name='expense_delete'),
]