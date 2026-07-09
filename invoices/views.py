from django.shortcuts import render, redirect, get_object_or_404
from income_expenses import forms
from django.contrib import messages
from PIL import Image
import pdfplumber
from .genai import Invoice_Analyse
from invoices.models import Invoice, Products, Store
from income_expenses.models import Expenses, AI_Usage
from datetime import datetime
import io
from django.db.models import Sum, Count
from django.db.models.functions import Lower
from django.contrib.auth.decorators import login_required
from income_expenses.decorators import AI_limit
import logging
from django.db import DatabaseError

logger = logging.getLogger(__name__)

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
            if page_text == '': # If it's empty, we don't need a list with empty strings.
                continue
            elif page_text:
                text += page_text + '\n'

            invoice_content.append(text)

    if invoice_content:
        return invoice_content

    elif not invoice_content:
        files_to_analyse = []
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                image = page.to_image()
                pil_image = image.original
                print(type(pil_image))
    
                files_to_analyse.append(pil_image)

        return files_to_analyse



def IMAGE_invoice(files):
    '''
    Reads the images with Pillow, and returns to analyse
    with gemini.
    Works with multiple image files.
    '''
    files_to_analyse = []
    for file in files:
        file.seek(0) # gets pointer at the beggining
        image = Image.open(file)

        # resize image, less tokens
        max_width = 1200
        width, height = image.size
        if width > max_width:
            wpercent = (max_width / float(width))
            hsize = int((float(height) * float(wpercent)))
            image = image.resize((max_width, hsize), Image.Resampling.LANCZOS)

            temp_buffer = io.BytesIO()
            image.save(temp_buffer, format="JPEG", quality=75, optimize=True)
            temp_buffer.seek(0) # pointer here
            
            compressed_image = Image.open(temp_buffer)

            files_to_analyse.append(compressed_image)
        else:
            files_to_analyse.append(image)

    return files_to_analyse


# Create your views here.
@login_required
@AI_limit
def invoice_reader(request):

    store_id = request.session.get('selected_store')
    store = get_object_or_404(Store, id=store_id, user=request.user)

    if request.method == 'POST':
        
        form = forms.UploadIncoiceForm(request.POST, request.FILES)

        if form.is_valid():
            files = request.FILES.getlist('invoice')  # Get all files (multiple files suitable for multipage invoice uploaded as images)
          

            files_to_analyse = []
            for file in files:

                if file.content_type == 'application/pdf':
                    to_genai = PDF_invoice(file)
                    data_to_db = Invoice_Analyse(to_genai)

                elif file.content_type in ['image/jpeg', 'image/png']:

                    logger.info('AI INVOICE - Read image file. Now goes to the function')
                    files_to_analyse.append(file)

                else:
                    messages.error(request, 'The uploaded file is not valid')

            if files_to_analyse:
                to_genai = IMAGE_invoice(files_to_analyse)
                logger.info('AI INVOICE - Function finished. Now goes to genai')
                try:
                    data_to_db = Invoice_Analyse(to_genai)
                except Exception as e:
                    logger.error(f'Gemini analyse error {e}')
                    messages.error(request,'Η ανάλυση του τιμολογίου αργεί περισσότερο απο ότι θα έπρεπε.'
                    'Δοκιμάστε ξανά αργότερα.')
                    return redirect('invoices:invoice_reader')


            if not data_to_db:
                logging.error(f"Invoice analysis failed.", exc_info=True)
                messages.error(request, 'Η ανάλυση τιμολογίου απέτυχε.')
                return redirect('invoices:invoice_reader')
            
            elif 'error' in data_to_db:
                logging.error(f"Invoice analysis failed: {data_to_db['error']}", exc_info=True)
                messages.error(request, f'Σφάλμα! {data_to_db['error']}')
                return redirect('invoices:invoice_reader')
            
            else: # No errors

                if data_to_db: # check if the invoice exists already in the database.
                    date_str = data_to_db["Ημερομηνία"]
                    date_to_db = datetime.strptime(date_str, '%d/%m/%Y').date() 


                    check_if_exists = Invoice.objects.filter(
                        store=store,
                        invoice_number__icontains=data_to_db["Αριθμός Τιμολογίου"],
                        afm__iexact=data_to_db["ΑΦΜ προμηθευτή"],
                        total__exact=data_to_db["Ποσά"]["Σύνολο πληρωτέο"],
                        date=date_to_db
                        ).exists()

                    
                    if check_if_exists:
                        messages.error(request, 'Το τιμολόγιο είναι ήδη καταχωρημένο')
                        return redirect('invoices:invoice_list')

                    else:
                        try:

                            AI_Usage.objects.create(store=store) # usage is autocreated inside the db.

                            expense = Expenses.objects.create(
                                store = store,
                                day = date_to_db,
                                amount = data_to_db["Ποσά"]["Σύνολο πληρωτέο"],
                                category = 'WITH_FPA_TAX',
                                comments = f'{data_to_db["Προμηθευτής"]} - Αυτόματη Καταχώρηση μέσω AI.'
                            )

                            invoice = Invoice.objects.create(
                                store = store,
                                expense = expense,
                                invoice_number = data_to_db["Αριθμός Τιμολογίου"],
                                afm = data_to_db["ΑΦΜ προμηθευτή"],
                                supplier = data_to_db["Προμηθευτής"],
                                date = date_to_db,
                                amount = data_to_db["Ποσά"]["ΚΑΘΑΡΗ ΑΞΙΑ"],
                                fpa = data_to_db["Ποσά"]["ΦΠΑ"],
                                total = data_to_db["Ποσά"]["Σύνολο πληρωτέο"]
                            )

                            for inv_products in data_to_db["Προϊόντα"]:
                                Products.objects.create(
                                    invoice_id = invoice,
                                    product_code = inv_products["Κωδικός προϊόντος"] or "N/A",
                                    name = inv_products["Όνομα προϊόντος"],
                                    unit = inv_products["Μονάδα μέτρησης"],
                                    price = inv_products["Τιμή προϊόντος"],
                                    quantity = inv_products["Ποσότητα"]
                                )



                            messages.success(request, 'Data Uploaded Successfully')

                            return redirect('invoices:invoice_list')
                        
                        except DatabaseError as e:
                            logger.error(f'Database Error {e}')
            
        else:
            messages.error(request, 'Invalid Form')

    else:
        form = forms.UploadIncoiceForm()
    return render(request, 'invoices/invoice_reader.html', {'form': form})

@login_required
def invoice_list(request):
    store_id = request.session.get('selected_store')
    store = get_object_or_404(Store, id=store_id, user=request.user)

    invoices = Invoice.objects.filter(store=store)
    context_to_html = {'invoices':invoices}
    return render(request, 'invoices/invoice_list.html', context=context_to_html)

@login_required
def invoice_details(request, id):
    invoice_detail = get_object_or_404(Invoice, id=id)
    products = invoice_detail.products.all()

    context_to_html = {
        'invoice_detail':invoice_detail,
        'products':products
    }
    return render(request, 'invoices/invoice_details.html', context=context_to_html)

@login_required
def delete_invoice(request, id):
    store_id = request.session.get('selected_store')
    store = get_object_or_404(Store, id=store_id, user=request.user)

    invoice = get_object_or_404(Invoice, store=store, id=id)
    if request.method == 'POST':
        if invoice.expense:
            invoice.expense.delete()

        invoice.delete()
        return redirect('invoices:invoice_list')
    else:
        return render (request, 'invoices/invoice_delete.html')

@login_required
def invoice_supplier_summary(request):
    store_id = request.session.get('selected_store')
    store = get_object_or_404(Store, id=store_id, user=request.user)

    if request.method == 'POST':
        selected_supplier = request.POST.get('supplier_select')
        print(selected_supplier)
        result = Invoice.objects.filter(store=store, supplier=selected_supplier)
        products = Products.objects.filter(invoice_id__in=result).annotate(name_cleaned=Lower('name'))\
            .values('name_cleaned', 'price', 'unit')\
            .annotate(total_quantity=Sum('quantity'))
        print(f'ΠΡΟΙΟΝΤΑ {products}')

        supplier = Invoice.objects.filter(store=store).values_list('supplier', flat=True)
        supplier = set(supplier)

        total_amount = Invoice.objects.filter(store=store, supplier=selected_supplier).aggregate(Sum('total'))

        context_to_html = {
            'products':products,
            'supplier':supplier,
            'selected_supplier':selected_supplier,
            'total_amount':total_amount,
        }

        return render(request, 'invoices/invoice_supplier.html', context=context_to_html)

    try:
        # flat=True returns a list. Without it returns a list with one tupple for each value.
        supplier = Invoice.objects.filter(store=store).values_list('supplier', flat=True).annotate(total_amount=Count('total'))
        supplier = set(supplier)

        context_to_html = {'supplier':supplier,}


    except Exception as e:
        logging.exception(f"Invoice supplier summary failed: {e}")
        messages.error(request, e)

    return render(request, 'invoices/invoice_supplier.html', context=context_to_html)
