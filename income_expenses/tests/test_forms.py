from django.test import TestCase
from django.contrib.auth.models import User
from accounts.forms import RegisterForm

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