from django.shortcuts import render, redirect, get_object_or_404
from income_expenses import forms
from django.contrib import messages
from PIL import Image
import pdfplumber
from .genai import Invoice_Analyse
from invoices.models import Invoice, Products, Store, Supplier
from income_expenses.models import Expenses, AI_Usage
from datetime import datetime
import io
from django.db.models import Sum, Count
from django.db.models.functions import Lower
from django.contrib.auth.decorators import login_required
from income_expenses.decorators import AI_limit
import logging
from django.db import DatabaseError
from income_expenses.forms import InvoiceUpdateForm, SupplierUpdateForm

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
@AI_limit()  # Parenthesis are used because we use a default redirect url on decorator.
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
                        supplier__afm=data_to_db["ΑΦΜ προμηθευτή"],
                        total__exact=data_to_db["Ποσά"]["Σύνολο πληρωτέο"],
                        date=date_to_db
                        ).exists()

                    
                    if check_if_exists:
                        messages.error(request, 'Το τιμολόγιο είναι ήδη καταχωρημένο')
                        return redirect('invoices:invoice_list')

                    else:
                        if data_to_db["Ποσά"]["ΦΠΑ"] == 24:
                            fpa_category = 'WITH_FPA_TAX'
                        elif data_to_db["Ποσά"]["ΦΠΑ"] == 13:
                            fpa_category = 'WITH_FPA_13'
                        elif data_to_db["Ποσά"]["ΦΠΑ"] == 6:
                            fpa_category = 'WITH_FPA_6'
                        else:
                            fpa_category = 'WITHOUT_FPA_TAX'
                            
                        try:

                            AI_Usage.objects.create(store=store) # usage is autocreated inside the db.

                            expense = Expenses.objects.create(
                                store = store,
                                day = date_to_db,
                                amount = data_to_db["Ποσά"]["Σύνολο πληρωτέο"],
                                category = fpa_category,
                                comments = f'{data_to_db["Προμηθευτής"]} - Αυτόματη Καταχώρηση μέσω AI.'
                            )

                            supplier_db, created = Supplier.objects.get_or_create(
                                afm = data_to_db["ΑΦΜ προμηθευτή"],
                                defaults={'supplier' : data_to_db["Προμηθευτής"]}
                            )

                            invoice = Invoice.objects.create(
                                store = store,
                                expense = expense,
                                invoice_number = data_to_db["Αριθμός Τιμολογίου"],
                                supplier = supplier_db,
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

    invoices = Invoice.objects.filter(store=store).order_by('-date')
    invoice_years = invoices.filter().dates('date','year',order='DESC')
    invoice_years = [y.year for y in invoice_years]

    if request.method == 'POST':
        selected_year = request.POST.get('selected_year')
        selected_month  = request.POST.get('selected_month')

        if selected_year:
            invoices = Invoice.objects.filter(store=store, date__year=selected_year).order_by('-date')

            invoice_month = invoices.dates('date','month',order='DESC')
            invoice_month = [i.month for i in invoice_month]
            if selected_month:
                invoices = invoices.filter(date__month=selected_month).order_by('-date')
        else:
            invoices = Invoice.objects.filter(store=store).order_by('-date')
            invoice_month = [] # crashes without it because it expects this value

        context_to_html = {
            'selected_year':selected_year,
            'selected_month':selected_month,
            'invoices': invoices,
            'invoice_years':invoice_years,
            'invoice_month':invoice_month,
        }

        return render(request, 'invoices/invoice_list.html', context=context_to_html)

    context_to_html = {
        'invoices':invoices,
        'invoice_years':invoice_years,
        'invoice_month':[],
    }
    return render(request, 'invoices/invoice_list.html', context=context_to_html)

# Need to check how to add on the invoice list. If I filter with the year or the supplier ??
@login_required
def paid_checkbox(request,id):
    inv = get_object_or_404(Invoice, id=id, store__user=request.user)
    # Changing 0 to 1 and 1 to 0 instead using if condition.
    inv.paid = not inv.paid
    inv.save(update_fields=['paid'])
    return redirect('invoices:invoice_list')

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

    invoice_years = Invoice.objects.filter(store=store).dates('date','year',order='DESC')
    invoice_years = [y.year for y in invoice_years]

    if request.method == 'POST':
        selected_year = request.POST.get('selected_year')
        selected_supplier_id = request.POST.get('supplier_select')
        
        if selected_year:
            result = Invoice.objects.filter(date__year=selected_year)
            result = result.filter(store=store, supplier=selected_supplier_id)
        else:
            result = Invoice.objects.filter(store=store, supplier=selected_supplier_id)


        products = Products.objects.filter(invoice_id__in=result).annotate(name_cleaned=Lower('name'))\
            .values('name_cleaned', 'price', 'unit')\
            .annotate(total_quantity=Sum('quantity'))

        if selected_year:
            supplier = Supplier.objects.filter(invoice__store=store,invoice__date__year=selected_year).distinct()
        else:
            supplier = Supplier.objects.filter(invoice__store=store).distinct()

        selected_supplier = get_object_or_404(Supplier, id=selected_supplier_id)

        total_amount = result.aggregate(Sum('total'))

        context_to_html = {
            'products':products,
            'supplier':supplier,
            'selected_supplier':selected_supplier,
            'total_amount':total_amount,
            'selected_year':selected_year,
            'invoice_years':invoice_years,
        }

        return render(request, 'invoices/invoice_supplier.html', context=context_to_html)

    try:
        # distinct returns unique values
        supplier = Supplier.objects.filter(invoice__store=store).distinct()

        context_to_html = {'supplier':supplier,'invoice_years':invoice_years,}


    except Exception as e:
        logging.exception(f"Invoice supplier summary failed: {e}")
        messages.error(request, e)

    return render(request, 'invoices/invoice_supplier.html', context=context_to_html)

def invoice_update(request, id):
    store_id = request.session.get('selected_store')
    store = get_object_or_404(Store, id=store_id, user=request.user)

    invoice = get_object_or_404(Invoice, id=id, store=store)
    products = invoice.products.all()

    
    if request.method == 'POST':
        form = InvoiceUpdateForm(request.POST, instance=invoice)
        old_total = invoice.total
        old_date = invoice.date
        if form.is_valid():
            form.save()

            total = form.cleaned_data.get('total')
            new_date = form.cleaned_data.get('date')

            if old_total != total:
                invoice.expense.amount = total
                
            if old_date != new_date:
                invoice.expense.day = new_date

            invoice.expense.save()

            messages.info(request, 'Οι αλλαγές πραγματοποιήθηκανε επιτυχώς!')

            return redirect('invoices:invoice_list')
        else:
            messages.error(request, 'Έχει γίνει κάποιο λάθος.')

    else:
        form = InvoiceUpdateForm(instance=invoice)
        context_to_html = {
            'form':form,
        }

        return render(request, 'invoices/invoice_update.html', context=context_to_html)

def supplier_update(request,id):
    store_id = request.session.get('selected_store')
    store = get_object_or_404(Store, id=store_id, user=request.user)

    supplier = get_object_or_404(Supplier, id=id)
    if request.method == 'POST':
        form = SupplierUpdateForm(request.POST, instance=supplier)
        form.save()

        messages.info(request, 'Οι αλλαγές πραγματοποιήθηκανε επιτυχώς!')
        return redirect('invoices:invoice_supplier')
    else:
        form = SupplierUpdateForm(instance=supplier)

        context_to_html = {
            'form':form,
        }
        return render(request, 'invoices/supplier_update.html', context=context_to_html)

