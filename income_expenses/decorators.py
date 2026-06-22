from datetime import datetime, timedelta
from django.shortcuts import render, redirect ,get_object_or_404
from models import Store, AIUsageLimit
from django.contrib import messages

def monthly_count(store):
    start_of_month = datetime.now().replace(day=1)
    result = AIUsageLimit.objects.filter(store=store, usage__gte=start_of_month).count()

    return result


def AI_limit(func):
    def wrapper(request):
        store_id = request.GET.get('selected_store')
        store = get_object_or_404(Store, id=store_id, user=request.user)
        AI_usage = get_object_or_404(AIUsageLimit, store=store, user=request.user)

        used_AI = monthly_count(store)

        if AI_usage.monthly_limit > used_AI:
            messages.error(request, 'Έχετε φτάσει το μηνιαίο όριο χρήσης του ΑΙ.')
            return redirect('invoices:invoice_reader')
        
    return wrapper


