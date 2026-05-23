from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from income_expenses.models import Store, Income, Expenses, FixedExpenses
from datetime import date

class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client() # Creates a fake browser
        self.user = User.objects.create(
            username = 'testuser',
            password = 'test1234',
            email = 'testemail@test.gr'
        )

    def test_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'username' : 'newuser',
            'email' : 'test@email.com',
            'password1' : 'VeryStrongPassword123!@#',
            'password2' : 'VeryStrongPassword123!@#'
        })
        
        new_user = User.objects.filter(username='newuser')
        self.assertTrue(new_user.exists())

class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        def test_login_with_correct_credentials(self):
            logged_in = self.client.login(username='testuser', password='testpass123')
            self.assertTrue(logged_in)

        def test_login_with_wrong_password(self):
            logged_in = self.client.login(username='testuser1', password='testpass1234')
            self.assertFalse(logged_in)

        def test_redirect_after_successful_login(self):
            response = self.client.post(reverse('accounts:login'), {
            'username' : 'testuser',
            'password' : 'testpass123'
        })
            self.assertEqual(response.status_code, 302) # 302 is redirect status

class SecurityTest(TestCase):
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

        # User 2

        self.user2 = User.objects.create_user(
            username='user2',
            password='user2pass'
        )

        self.client2 = Client()  # Need seperate client for diferrent user
        self.client2.login(username='user2', password='user2pass')
    
    def test_if_different_user_has_access(self):

        # store_url = reverse('income_expenses:detail', args=[self.store.id]) # args puts the id on the url's id section
        # response = client2.get(store_url)

        # store_url = reverse('income_expenses:update_store', args=[self.store.id])
        # response = client2.get(store_url)

        # self.assertNotEqual(response.status_code, 200)
        delete_url = reverse('income_expenses:delete_store', args=[self.store.id])
        response = self.client2.post(delete_url)
        
        self.assertNotEqual(response.status_code, 200)
        
        # Verify store isn't deleted
        self.assertTrue(Store.objects.filter(id=self.store.id).exists())

    def test_if_different_user_can_see_income(self):
        add_income = Income.objects.create(
            store = self.store,
            day = '2026-05-01',
            income_cash = 200,
            income_pos = 100,
            income_other = 50
        )

        check_income = reverse('income_expenses:detail', args=[add_income.id])
        response = self.client2.get(check_income)
        self.assertNotEqual(response.status_code, 200)

    def test_if_different_user_can_see_expense(self):
        add_expense = Expenses.objects.create(
            store = self.store,
            day = '2026-05-01',
            amount = 200,
            category = 'test',
            comments = 'testing...'
        )

        check_expense = reverse('income_expenses:expenses_detail', args=[add_expense.id])
        response = self.client2.get(check_expense)
        self.assertNotEqual(response.status_code, 200)

    def test_if_different_user_can_delete_income(self):
        add_income = Income.objects.create(
            store = self.store,
            day = '2026-05-01',
            income_cash = 200,
            income_pos = 100,
            income_deposit = 25,
            income_check = 25,
            income_other = 50,
            comments = 'testing...'
        )

        delete_income = reverse('income_expenses:income_delete', args=[add_income.id])
        response = self.client2.post(delete_income)
        self.assertNotEqual(response.status_code, 200)

        self.assertTrue(Income.objects.filter(id=add_income.id).exists())

    def test_if_different_user_can_update_income(self):
        add_income = Income.objects.create(
            store = self.store,
            day = '2026-05-01',
            income_cash = 200,
            income_pos = 100,
            income_deposit = 25,
            income_check = 25,
            income_other = 50,
            comments = 'testing...'
        )

        update_income = reverse('income_expenses:income_update', args=[add_income.id])
        response = self.client2.post(update_income, {
            'income_cash':500,
            'income_other':50,
        })

        self.assertNotEqual(response.status_code, 200)

    def test_if_different_user_can_delete_expense(self):
        add_expense = Expenses.objects.create(
            store = self.store,
            day = '2026-05-01',
            amount = 200,
            category = 'test',
            comments = 'testing...'
        )

        delete_expense = reverse('income_expenses:expense_delete', args=[add_expense.id])
        response = self.client2.post(delete_expense)
        self.assertNotEqual(response.status_code, 200)

        self.assertTrue(Expenses.objects.filter(id=add_expense.id).exists())

    def test_if_different_user_can_update_expense(self):
        add_expense = Expenses.objects.create(
            store = self.store,
            day = '2026-05-01',
            amount = 200,
            category = 'test',
            comments = 'testing...'
        )

        update_expense = reverse('income_expenses:expense_update', args=[add_expense.id])
        response = self.client2.post(update_expense, {
            'amount':500,
            'category':'test2',
        })

        self.assertNotEqual(response.status_code, 200)

    def test_if_different_user_can_see_fixed_expenses(self):
        fixed_expense = FixedExpenses.objects.create(
            store=self.store,
            name='fixed test',
            amount=50,
            frequency='MONTHLY',
            start_date=date.today(),
            next_charge_date='2026-06-21'
        )

        check_fixed_expense = reverse('income_expenses:fixed_expenses')
        response = self.client2.get(check_fixed_expense)
        self.assertNotEqual(response.status_code, 200)

    def test_if_different_user_can_delete_fixed_expenses(self):
        fixed_expense = FixedExpenses.objects.create(
            store=self.store,
            name='fixed test',
            amount=50,
            frequency='MONTHLY',
            start_date=date.today(),
            next_charge_date='2026-06-21'
        )

        delete_fixed_expense = reverse('income_expenses:delete_fixed_expense', args=[fixed_expense.id])
        response = self.client2.post(delete_fixed_expense)
        self.assertNotEqual(response.status_code, 200)

        self.assertTrue(FixedExpenses.objects.filter(id=fixed_expense.id).exists())

from unittest.mock import patch
from datetime import date
class ViewsTest(TestCase):

    def test_index_on_first_day_of_month(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

        # Create a store for the user
        store = Store.objects.create(name='Test Store', user=user)
        
        session = self.client.session
        session['selected_store'] = store.id
        session.save()

        # Mock and patch predends it's a different date
        with patch('income_expenses.views.date') as mock_date:
            mock_date.today.return_value = date(2026, 5, 1)
            response = self.client.get(reverse('income_expenses:index'))

        self.assertEqual(response.status_code, 200)