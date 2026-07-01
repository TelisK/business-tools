from django.shortcuts import render
from income_expenses.decorators import AI_limit
from django.contrib.auth.decorators import login_required

# Create your views here.
@AI_limit
@login_required
def AI_chat(request):
    pass