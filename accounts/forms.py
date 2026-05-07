from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms # error forms

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']
        
    # clean email checks if the email exists. If it exists user cannot register and gets a message.
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email