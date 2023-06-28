from django import forms

class TransferForm(forms.Form):
    username = forms.CharField()
    amount = forms.DecimalField(min_value=0.01, max_value=999999999999.99)

class RequestForm(forms.Form):
    username = forms.CharField()
    amount = forms.DecimalField(min_value=0.01, max_value=999999999999.99)