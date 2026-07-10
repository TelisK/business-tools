from django.utils import timezone
from django.shortcuts import render, redirect ,get_object_or_404
from .models import Store, AI_Usage, AI_Limit
from django.contrib import messages

def monthly_count(store):
    '''
    Counts the monthly usage of AI and returns how many times user used these features.
    '''
    start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0)
    result = AI_Usage.objects.filter(store=store, usage__gte=start_of_month).count()

    return result


def AI_limit(redirect_url='invoices:invoice_list'):
    '''
    Decorator for calculating and limitate the usage of AI features.
    Using default redirect url, and the ability to use a different url
    on a different view.
    '''
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            store_id = request.session.get('selected_store')
            store = get_object_or_404(Store, id=store_id, user=request.user)

            used_AI = monthly_count(store)

            ai_limit_object, created = AI_Limit.objects.get_or_create(
                store=store,
                defaults={'monthly_limit': 10} # Used only when creating new limit
            )

            if used_AI >= ai_limit_object.monthly_limit:
                messages.error(request, 'Έχετε φτάσει το μηνιαίο όριο χρήσης του ΑΙ.')
                return redirect(redirect_url)

            return func(request, *args, **kwargs)
        return wrapper
    return decorator


