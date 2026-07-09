from django.shortcuts import render, get_object_or_404, redirect
from income_expenses.decorators import AI_limit
from django.contrib.auth.decorators import login_required
from .agent import gemini_agent
from django.http import JsonResponse
from income_expenses.models import Store
import logging

logger = logging.getLogger(__name__)

# Create your views here.
@login_required
@AI_limit
def AI_chat(request):
    store_id = request.session.get('selected_store')
    user_store = get_object_or_404(Store, id=store_id, user=request.user)

    if request.method == 'POST':
        try:
            user_prompt = request.POST.get('prompt')
            print(f"[DEBUG] Η ερώτηση που πήραμε από τη φόρμα είναι: {user_prompt}")
            if user_prompt:
                # Bug was asking for the store id all the time. So I integrate with user prompt.
                final_prompt = f'Για το κατάστημα με id {store_id}, {user_prompt}'
                ai_response = gemini_agent(store_id, final_prompt)
                print(f"[DEBUG] Η απάντηση του Gemini είναι: {ai_response}")
                
                context = {
                    'prompt': user_prompt,
                    'answer': ai_response,
                    'store': user_store,
                }
                return render(request, 'ai_assistant/chat.html', context=context)
            
        except Exception as e:
            logger.error(f'AI Assistant Error {e}')
            return redirect('ai_assistant:chat')

    return render(request, 'ai_assistant/chat.html', {'store':user_store})
