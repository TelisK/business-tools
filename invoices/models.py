from django.db import models
from income_expenses.models import Store

# Create your models here.

class Invoice(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    invoice_number = models.CharField(null=False, max_length=50)
    afm = models.CharField(max_length=9)
    supplier = models.CharField(max_length=200)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fpa = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    file = models.FileField(upload_to='invoices/', null=True, blank=True)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.supplier}  --  {self.date} : {self.total}'

class Products(models.Model):
    # with related_name i can do invoice.products.all() instead of Product.objects.filter(invoice=invoice)
    invoice_id = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='products')
    product_code = models.CharField(max_length=50, null=False)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.FloatField()

    def __str__(self):
        return f'{self.invoice_id.supplier} : {self.name} -- {self.price} -- {self.price}'