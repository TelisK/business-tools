from django.shortcuts import render, redirect, get_object_or_404
from income_expenses import forms
from django.contrib import messages
from PIL import Image
import pdfplumber
from .genai import Invoice_Analyse
from invoices.models import Invoice, Products, Store
from income_expenses.models import Expenses
from datetime import datetime


def PDF_invoice(pdf_file):
    '''
    Reads the pdf file to analyse it later with gemini.
    If the pdf is not a picture, I am using pdfplumber to
    export the text.
    If the pdf is from a picture, I am using Pillow to export
    the image file.
    '''

    invoice_content = []
    text = ''
    pdf_file.seek(0)
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'

            invoice_content.append(text)

    if invoice_content:
        return invoice_content

    elif not invoice_content:
        files_to_analyse = []
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf:
                image = page.to_image()
                files_to_analyse.append(image)

        return files_to_analyse



def IMAGE_invoice(files):
    files_to_analyse = []
    for file in files:
        file.seek(0) # gets pointer at the beggining
        image = Image.open(file)
        files_to_analyse.append(image)
    return files_to_analyse


# Create your views here.
def invoice_reader(request):

    store_id = request.session.get('selected_store')
    store = get_object_or_404(Store, id=store_id, user=request.user)

    if request.method == 'POST':
        
        form = forms.UploadIncoiceForm(request.POST, request.FILES)

        if form.is_valid():
            files = request.FILES.getlist('invoice')  # Get all files (multiple files suitable for multipage invoice uploaded as images)
            #file = request.FILES['invoice']
            
            print(f"Files count: {len(files)}")  # Debug multiple files
            print(f"Files: {files}")  # Debug multiple files

            files_to_analyse = []
            for file in files:
            
                print(f"Processing: {file.name}, Type: {file.content_type}")

                if file.content_type == 'application/pdf':
                    to_genai = PDF_invoice(file)
                    data_to_db = Invoice_Analyse(to_genai)

                elif file.content_type in ['image/jpeg', 'image/png']:

                    print('Read image file. Now goes to the function')
                    files_to_analyse.append(file)

                else:
                    messages.error(request, 'The uploaded file is not valid')

            if files_to_analyse:
                to_genai = IMAGE_invoice(files_to_analyse)
                print('Function finished. Now goes to genai')
                data_to_db = Invoice_Analyse(to_genai)

            # if data_to_db['status'] == 'error':  # error handling in case gemini is busy
            #     messages.error(request, data_to_db['message'])

            # elif not data_to_db:  # error handling in case gemini finds no data


            if not data_to_db:
                messages.error(request, 'Η ανάλυση τιμολογίου απέτυχε.')
                return redirect('invoices:invoice_reader')
            
            elif data_to_db:
                check_if_exists = Invoice.objects.filter(
                    invoice_number__iexact=data_to_db["Αριθμός Τιμολογίου"],
                    afm__iexact=data_to_db["ΑΦΜ προμηθευτή"],
                    total__exact = data_to_db["Ποσά"]["Σύνολο πληρωτέο"]
                    ).exists()
                
                if check_if_exists == True:
                    messages.error(request, 'Το τιμολόγιο είναι ήδη καταχωρημένο')
                    return redirect('invoices:invoice_list')

            else:
                date_str = data_to_db["Ημερομηνία"]
                date_to_db = datetime.strptime(date_str, '%d/%m/%Y').date()

                invoice = Invoice.objects.create(
                    store = store,
                    invoice_number = data_to_db["Αριθμός Τιμολογίου"],
                    afm = data_to_db["ΑΦΜ προμηθευτή"],
                    supplier = data_to_db["Προμηθευτής"],
                    date = date_to_db,
                    amount = data_to_db["Ποσά"]["ΚΑΘΑΡΗ ΑΞΙΑ"],
                    fpa = data_to_db["Ποσά"]["ΦΠΑ"],
                    total = data_to_db["Ποσά"]["Σύνολο πληρωτέο"]
                )

                Expenses.objects.create(
                    store = store,
                    day = date_to_db,
                    amount = data_to_db["Ποσά"]["Σύνολο πληρωτέο"],
                    category = 'Τιμολόγια',
                    comments = 'Αυτόματη Καταχώρηση μέσω AI.'
                )

                for inv_products in data_to_db["Προϊόντα"]:
                    Products.objects.create(
                        invoice_id = invoice,
                        product_code = inv_products["Κωδικός προϊόντος"],
                        name = inv_products["Όνομα προϊόντος"],
                        unit = inv_products["Μονάδα μέτρησης"],
                        price = inv_products["Τιμή προϊόντος"],
                        quantity = inv_products["Ποσότητα"]
                    )



                messages.success(request, 'Data Uploaded Successfully')

                return redirect('invoices:invoice_list')
            
        else:
            messages.error(request, 'Invalid Form')

    else:
        form = forms.UploadIncoiceForm()
    return render(request, 'invoices/invoice_reader.html', {'form': form})

def invoice_list(request):
    return render(request, 'invoices/invoice_list.html')