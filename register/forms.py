from django import forms
from payapp.models import Currency

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

class RegisterForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()

    currencies = Currency.objects.all()
    currency = forms.ModelChoiceField(queryset=currencies, empty_label=None, to_field_name="currency_code")
