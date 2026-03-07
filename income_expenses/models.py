from django.db import models

# Create your models here.
class Income(models.Model):
        
    day = models.DateField(unique=True)
    income_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    income_pos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    income_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    income_check = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    income_other = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comments = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.day) + ' : ' + str(self.income_sum) + ' €'
    
    @property
    def income_sum(self):
        return self.income_cash + self.income_pos + self.income_deposit + self.income_check + self.income_other

class Expenses(models.Model):

    def __str__(self):
        return str(self.day) + ' : ' + str(self.amount) + ' €'

    day = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, blank=True)
    comments = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)