from django.shortcuts import render, redirect
from income_expenses import forms
from django.contrib import messages
from PIL import Image
import pdfplumber
from genai import Invoice_Analyse


def PDF_invoice(files):
    invoice_content = []
    for file in files:
        text = ''
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'

        invoice_content.append(text)

    if invoice_content:
        return invoice_content

    elif not invoice_content:
        files_to_analyse = []
        with pdfplumber.open(file) as pdf:
            for page in pdf:
                image = page.to_image()
                files_to_analyse.append(image)

        return files_to_analyse



def IMAGE_invoice(files):
    files_to_analyse = []
    for file in files:
        image = Image.open(file)
        files_to_analyse.append(image)
    return files_to_analyse


# Create your views here.
def invoice_reader(request):
    if request.method == 'POST':
        form = forms.UploadIncoiceForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('files')  # Get all files (multiple files suitable for multipage invoice uploaded as images)
            #file = request.FILES['invoice']
            
            for file in files:
                if file.content_type == 'application/pdf':
                    to_genai = PDF_invoice(file)
                    Invoice_Analyse(to_genai)

                elif file.content_type == 'image/jpeg' or 'image/png':
                    to_genai = IMAGE_invoice(file)
                    Invoice_Analyse(to_genai)
                    
                else:
                    messages.error(request, 'The uploaded file is not valid')

            return redirect('invoices:invoice_list')
            
        else:
            messages.error(request, 'Invalid Form')

    else:
        form = forms.UploadIncoiceForm()
    return render(request, 'invoices/invoice_reader.html', {'form': form})