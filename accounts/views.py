from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegisterForm()
        if form.is_valid:
            new_user = form.save()
            messages.success('Thank you for registration! You are now logged in.')
            new_user = authenticate(username = form.cleaned_data['username'],
                                    password = form.cleaned_data['password1'],)
            
            login(request, new_user)
            redirect('income_expenses/index.html')

    form = RegisterForm()
    return render(request, 'acoounts:register.html', {form:form}) 

