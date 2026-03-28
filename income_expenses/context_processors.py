from .models import Store

def stores_context(request):
    if request.user.is_authenticated:
        stores_list = Store.objects.filter(user=request.user)
        store_id = request.session.get('selected_store', None)
        store = stores_list.filter(id=store_id).first() if store_id else stores_list.first()
        return {
            'stores_list': stores_list,
            'current_store': store,
        }
    else:
        return {}