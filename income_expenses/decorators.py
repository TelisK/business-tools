from datetime import datetime, timedelta
from django.shortcuts import render, redirect ,get_object_or_404
from .models import Store, AI_Usage, AI_Limit
from django.contrib import messages

def monthly_count(store):
    '''
    Counts the monthly usage of AI and returns how many times user used these features.
    '''
    start_of_month = datetime.now().replace(day=1)
    result = AI_Usage.objects.filter(store=store, usage__gte=start_of_month).count()

    return result


def AI_limit(func):
    '''
    Decorator for calculating and limitate the usage of AI features.
    '''
    def wrapper(request, *args, **kwargs):
        store_id = request.session.get('selected_store')
        print(f'STORE ID = {store_id}')
        store = get_object_or_404(Store, id=store_id, user=request.user)
        print(f'STORE = {store}')
        used_AI = monthly_count(store)



        ai_limit_object, created = AI_Limit.objects.get_or_create(
            store=store,
            defaults={'monthly_limit': 10} # Used only when creating new limit
        )

        if used_AI >= ai_limit_object.monthly_limit:
            messages.error(request, 'Έχετε φτάσει το μηνιαίο όριο χρήσης του ΑΙ.')
            return redirect('invoices:invoice_list')

        return func(request, *args, **kwargs)
    return wrapper


