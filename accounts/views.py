from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from income_expenses.models import Store
import logging

logger = logging.getLogger(__name__)

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            logger.info(f'User with username {form.cleaned_data['username']} registered.')
            messages.success(request, 'Thank you for registration! You are now logged in.')
            new_user = authenticate(username = form.cleaned_data['username'],
                                    password = form.cleaned_data['password1'],)
            
            login(request, new_user)
            return redirect('income_expenses:index')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form':form}) 

@login_required
def delete_account(request):
    user = request.user
    if request.method == 'POST':
        logger.info(f'User with username {user} delete the account premanently.')
        logout(request)
        user.delete()
        messages.success(request, 'Ο λογαριασμός διαγράφηκε οριστικά!')
        return redirect('accounts:register')
    else:
        return render(request, 'accounts/delete_account.html')
