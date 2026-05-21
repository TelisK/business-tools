from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from income_expenses.models import Store, Income

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
            self.assertEqual(response.status_code, 302)

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
    
    def test_if_different_user_has_access(self):
        user2 = User.objects.create_user(
            username='user2',
            password='user2pass'
        )

        client2 = Client()  # Need seperate client for diferrent user
        client2.login(username='user2', password='user2pass')

        store_url = reverse('income_expenses:detail', args=[self.store.id]) # args puts the id on the url's id section
        response = client2.get(store_url)

        self.assertNotEqual(response.status_code, 200)