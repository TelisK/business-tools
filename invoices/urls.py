"""
URL configuration for business_tools project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

app_name = 'invoices'


urlpatterns = [
    path('', views.invoice_reader, name='invoice_reader'),
    path('<int:id>/invoice_details/', views.invoice_details, name='invoice_details'),
    path('invoice_list/', views.invoice_list, name='invoice_list'),
    path('invoice_delete/<int:id>/', views.delete_invoice, name='invoice_delete'),
    path('invoice_supplier/', views.invoice_supplier_summary, name='invoice_supplier'),
]