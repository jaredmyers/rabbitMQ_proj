from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(label='User Name')
    pw = forms.CharField(label="Password")
    pw2 = forms.CharField(label="Retype Password")

class LoginForm(forms.Form):
    username = forms.CharField(label='User Name')
    pw = forms.CharField(label="Password")