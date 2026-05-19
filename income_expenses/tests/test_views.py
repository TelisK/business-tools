from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

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
            'password1' : 'testpass',
            'password2' : 'testpass'
        })
        
        new_user = User.objects.filter(username='newuser')
        self.assertTrue(new_user.exists())