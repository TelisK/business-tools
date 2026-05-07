from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            messages.success(request, 'Thank you for registration! You are now logged in.')
            new_user = authenticate(username = form.cleaned_data['username'],
                                    password = form.cleaned_data['password1'],)
            
            login(request, new_user)
            return redirect('income_expenses:index')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form':form}) 
