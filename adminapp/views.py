from django.db import transaction, OperationalError
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from payapp.models import Transfer, Wallet
from register.forms import RegisterForm
from django.contrib import messages
from django.urls import reverse
import requests

# Create your views here.

@login_required()
def register(request):
    if request.user.is_staff != True:
        return redirect("/")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            email = form.cleaned_data["email"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            currency = form.cleaned_data["currency"]

            try:
                r = requests.get(request.build_absolute_uri(reverse("convert-api", args=["GBP", currency.currency_code, "1000.00"])))

                if r.status_code == 400:
                    raise ValueError("Something went wrong")

                r = r.json()

                with transaction.atomic():
                    user = User.objects.create_user(username, email, password)
                    user.first_name = first_name
                    user.last_name = last_name
                    user.is_staff = True
                    user.save()
                    Wallet.objects.create(currency=currency, balance=r["exchanged_amount"], user=user)
                    messages.success(request, "Registration Successful")

            except OperationalError:
                messages.error(request, f"Transfer operation is not possible now.")
            except ValueError as e:
                messages.error(request, e)

    else:
        form = RegisterForm()
    return render(request, "adminapp/register.html", {
        "form": form,
    })

@login_required()
def users(request):
    if request.user.is_staff != True:
        return redirect("/")

    users = User.objects.all()

    return render(request, "adminapp/users.html", {
        "users": users
    })

@login_required()
def history(request):
    if request.user.is_staff != True:
        return redirect("/")

    transfers = Transfer.objects.all()

    return render(request, "adminapp/transfers.html", {
        "transfers": transfers
    })
