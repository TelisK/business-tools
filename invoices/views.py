from django.shortcuts import render
from income_expenses import forms

# Create your views here.
def invoice_reader(request):
    if request.method == 'POST':
        form = forms.UploadIncoiceForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['invoice']
            print(file)
            print(type(file))
            print(file.name)
            #file_extension = file.split('.')
    else:
        form = forms.UploadIncoiceForm()
    return render(request, 'invoices/invoice_reader.html', {'form': form})