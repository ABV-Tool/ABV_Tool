# authentication/forms.py
from django import forms

# template for custom login form
class LoginForm(forms.Form):
    username = forms.CharField(label="Benutzername", max_length=63, required=True, widget=forms.TextInput(attrs={'class': 'mb-3'}))
    password = forms.CharField(label="Passwort", max_length=63, required=True, widget=forms.PasswordInput)