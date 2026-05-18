from django.test import TestCase
from django.contrib.auth.models import User
from income_expenses.models import Store, Income, Expenses, FixedExpenses

# Create your tests here.

class IncomeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        
        self.store = Store.objects.create(
            name='test store',
            user=self.user
        )
    
    def test_income_sum(self):
        income = Income.objects.create(
            store=self.store,
            day='2026-01-01',
            income_cash=100,
            income_pos=50,
            income_deposit=50,
            income_check=25,
            income_other=25
        )

        expected_sum = 250
    

        self.assertEqual(income.income_sum, expected_sum)

