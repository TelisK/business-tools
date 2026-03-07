from django.urls import path
from . import views

app_name = 'income_expenses'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:id>/', views.detail, name='detail'),
    path('add_income/', views.submit_income, name='submit_income'),
    path('add_expense/', views.submit_expense, name='submit_expense'),
    path('add_store/', views.add_store, name='add_store'),
]