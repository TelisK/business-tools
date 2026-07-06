from django.shortcuts import render
from income_expenses.decorators import AI_limit
from django.contrib.auth.decorators import login_required
from .agent import gemini_agent
from django.http import JsonResponse

# Create your views here.
@AI_limit
@login_required
def AI_chat(request):
    user_prompt = request.GET.get('prompt')

    user_store = request.store.id

    ai_response = gemini_agent(user_store, user_prompt)

    return JsonResponse({'response': ai_response})
