from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Store(models.Model):
    name = models.TextField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'user')

    def __str__(self):
        return self.name

class Income(models.Model):
        
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True)
    day = models.DateField()
    income_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    income_pos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    income_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    income_check = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    income_other = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comments = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['store','day']


    def __str__(self):
        return f"{self.day} : {self.income_sum} €"
    
    @property  # creates sum from the data on the database. Best way in case the data are updated later.
    def income_sum(self):
        return self.income_cash + self.income_pos + self.income_deposit + self.income_check + self.income_other

class Expenses(models.Model):
    class Meta:
        verbose_name_plural = 'expenses'
        verbose_name = 'expense'

    def __str__(self):
        return f"{self.day} : {self.amount} €"

    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    day = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, blank=True)
    comments = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class FixedExpenses(models.Model):

    def __str__(self):
        return f'{self.store.name} - {self.name} : {self.amount} - {self.frequency}'
    
    FIXED_EXPENSES_CHOICES = [
        ('DAILY','Daily'),
        ('WEEKLY','Weekly'),
        ('MONTHLY','Monthly'),
        ('ANNUAL','Annual')
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(choices=FIXED_EXPENSES_CHOICES, default='MONTHLY')
    start_date = models.DateField()
    next_charge_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)



