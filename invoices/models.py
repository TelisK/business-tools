from django.db import models
from income_expenses.models import Store, Expenses
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Supplier(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    # db_index links with the other table and is faster.
    afm = models.CharField(max_length=9, unique=True, db_index=True)
    supplier = models.CharField(max_length=200)

class Invoice(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    # PROTECT because Supplier will be common with all users who have the same. We don't want to be deleted.
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    expense = models.OneToOneField(Expenses, on_delete=models.CASCADE, blank=True, null=True)
    invoice_number = models.CharField(null=False, max_length=50)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fpa = models.DecimalField(max_digits=10, decimal_places=2)
    fpa_persentage = models.IntegerField(default=24, 
                            validators=[MinValueValidator(0), MaxValueValidator(100)])
    total = models.DecimalField(max_digits=10, decimal_places=2)
    file = models.FileField(upload_to='invoices/', null=True, blank=True)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.supplier}  --  {self.date} : {self.total}'

class Products(models.Model):
    class Meta:
        verbose_name_plural = 'products'
        verbose_name = 'product'

    # with related_name i can do invoice.products.all() instead of Product.objects.filter(invoice=invoice)
    invoice_id = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='products')
    product_code = models.CharField(max_length=50, null=False)
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.FloatField()

    def __str__(self):
        return f'{self.invoice_id.supplier} : {self.name} -- {self.price} -- {self.quantity}'