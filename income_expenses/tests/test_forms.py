from django.test import TestCase, Client
from django.contrib.auth.models import User
from accounts.forms import RegisterForm
from income_expenses.forms import IncomeForm, ExpenseForm
from datetime import date
from income_expenses.models import Store

class RegisterFormTest(TestCase):
    def test_if_data_is_valid(self):
        form = RegisterForm(data={
            'username' : 'newuser',
            'email' : 'test@email.com',
            'password1' : 'VeryStrongPassword123!@#',
            'password2' : 'VeryStrongPassword123!@#'
        })
        self.assertTrue(form.is_valid())

    def test_if_passwords_are_different(self):
        form = RegisterForm(data={
            'username' : 'newuser',
            'email' : 'test@email.com',
            'password1' : 'VeryStrongPassword123!@#',
            'password2' : 'VeryveryStrongPassword12345!@#'
        })      
        self.assertFalse(form.is_valid())

    def test_if_email_exists(self):
        User.objects.create(
            username = 'existing_user',
            email = 'test@email.com',
            password = 'mypassword'
        )

        form = RegisterForm(data={
            'username' : 'newuser',
            'email' : 'test@email.com',
            'password1' : 'VeryStrongPassword123!@#',
            'password2' : 'VeryStrongPassword123!@#'
        })    

        self.assertFalse(form.is_valid())

class IncomeFormTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.store = Store.objects.create(
            name='test store',
            user=self.user
        )

    def test_if_data_is_valid(self):
        form = IncomeForm(data={
            'store':self.store.id,
            'day':date.today(),
            'income_cash':50,
            'income_pos':50,
            'income_deposit':50,
            'income_check':50,
            'income_other':50,
            'comments':'test'
        })

        self.assertTrue(form.is_valid())

    def test_if_missing_day_fails(self):
        form = IncomeForm(data={
            'store':self.store.id,
            'income_cash':50,
            'income_pos':50,
            'income_deposit':50,
            'income_check':50,
            'income_other':50,
            'comments':'test'
        })

        self.assertFalse(form.is_valid())

    def test_if_decimal_amounts_works(self):
        form = IncomeForm(data={
            'store':self.store.id,
            'day':date.today(),
            'income_cash':50.30,
            'income_pos':50.20,
            'income_deposit':50.40,
            'income_check':50.60,
            'income_other':50.70,
            'comments':'test'
        })

        self.assertTrue(form.is_valid())

class ExpensesFormTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.store = Store.objects.create(
            name='test store',
            user=self.user
        )

    def test_if_data_is_valid(self):
        form = ExpenseForm(data={
            'store':self.store.id,
            'day':date.today(),
            'amount':500.50,
            'category':'test category',
            'comments':'test comments'
        })
        
        self.assertTrue(form.is_valid())

    def test_if_missing_day_fails(self):
        form = ExpenseForm(data={
            'store':self.store.id,
            'amount':500.50,
            'category':'test category',
            'comments':'test comments'
        })

        self.assertFalse(form.is_valid())