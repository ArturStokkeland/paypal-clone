from django.db import transaction, OperationalError
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import LoginForm, RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from payapp.models import Wallet, Currency
from django.contrib import messages
import requests


# Create your views here.

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                None
                #user does not exist


    else:
        form = LoginForm()
    return render(request, "register/login.html", {
        "form": form,
    })

def register_view(request):
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
                    user.save()
                    Wallet.objects.create(currency=currency, balance=r["exchanged_amount"], user=user)
                    login(request, user)
                    return redirect("/")

            except OperationalError:
                messages.error(request, f"Transfer operation is not possible now.")
            except ValueError as e:
                messages.error(request, e)

    else:
        form = RegisterForm()
    return render(request, "register/register.html", {
        "form": form,
    })

def logout_view(request):
    logout(request)
    return redirect(reverse("login-page"))

def init(request):
    Currency.objects.create(currency_name="United States Dollar", currency_code="USD", currency_symbol="$", exchange_rate_to_GBP=0.800)
    Currency.objects.create(currency_name="Euro", currency_code="EUR", currency_symbol="€", exchange_rate_to_GBP=0.880)
    Currency.objects.create(currency_name="Japanese Yen", currency_code="JPY", currency_symbol="¥", exchange_rate_to_GBP=0.006)
    Currency.objects.create(currency_name="Sterling", currency_code="GBP", currency_symbol="£", exchange_rate_to_GBP=1.000)
    Currency.objects.create(currency_name="Renminbi", currency_code="CNY", currency_symbol="¥", exchange_rate_to_GBP=0.120)
    Currency.objects.create(currency_name="Australian Dollar", currency_code="AUD", currency_symbol="A$", exchange_rate_to_GBP=0.530)
    Currency.objects.create(currency_name="Canadian Dollar", currency_code="CAD", currency_symbol="C$", exchange_rate_to_GBP=0.590)

    User.objects.create_superuser(username="admin1", password="admin1", email="admin1@payapp.com")

    gbp = Currency.objects.get(currency_code="GBP")
    user = User.objects.get(username="admin1")
    user.first_name = "John"
    user.last_name = "Doe"
    user.save()

    Wallet.objects.create(currency=gbp, balance=1000.00, user=user)

    return redirect("/admin")
