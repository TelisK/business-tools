from django.test import TestCase
from django.contrib.auth.models import User
from income_expenses.models import Store, Income, Expenses, FixedExpenses
from django.db import IntegrityError
from datetime import date


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

    def test_duplicate_income_unique_together(self):
        income2 = Income.objects.create(
            store=self.store,
            day='2026-01-01',
            income_cash=50,
            income_pos=0,
            income_deposit=0,
            income_check=0,
            income_other=0
        )

        self.assertRaises(IntegrityError)
    
    def test_default_values(self):
        income3 = Income.objects.create(
            store=self.store,
            day='2026-05-01',
            comments='test'
        )

        self.assertEqual(income3.income_cash, 0)
        self.assertEqual(income3.income_pos, 0)
        self.assertEqual(income3.income_deposit, 0)
        self.assertEqual(income3.income_check, 0)
        self.assertEqual(income3.income_other, 0)

        



class StoreModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

    def test_store_creation(self):
        store_name = Store.objects.create(
            name = 'test store',
            user = self.user
        )

        self.assertEqual(store_name.name, 'test store')
        self.assertEqual(store_name.user, self.user)



