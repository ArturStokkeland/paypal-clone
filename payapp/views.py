import decimal

from django.db import transaction, OperationalError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from payapp.forms import TransferForm, RequestForm
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import Transfer, Request
import requests

# Create your views here.

@login_required(redirect_field_name="")
def index(request):
    return render(request, "payapp/index.html")

@login_required(redirect_field_name="")
def history(request):

    transfers = Transfer.objects.filter(sender=request.user) | Transfer.objects.filter(recipient=request.user)

    return render(request, "payapp/history.html", {
        "transfers": transfers
    })

@login_required(redirect_field_name="")
def pending(request):

    received = Request.objects.all().filter(payer=request.user, status="Pending")
    sent = Request.objects.all().filter(requester=request.user, status="Pending")

    return render(request, "payapp/pending.html", {
        "received": received,
        "sent": sent,
    })

@login_required(redirect_field_name="")
def transfer(request):

    if request.method == "POST":
        form = TransferForm(request.POST)

        if form.is_valid():
            to_user = form.cleaned_data["username"]
            amount = form.cleaned_data["amount"]
            try:
                sender = User.objects.select_for_update().get(username=request.user.username)
                recipient = User.objects.select_for_update().get(username=to_user)

                if sender.wallet.balance < amount:
                    raise ValueError("Not enough funds.")

                if sender == recipient:
                    raise ValueError("You can't send money to yourself")

                r = requests.get(request.build_absolute_uri(reverse("convert-api", args=[sender.wallet.currency.currency_code, recipient.wallet.currency.currency_code, amount])))

                if r.status_code == 400:
                    raise ValueError("Something went wrong")

                r = r.json()

                with transaction.atomic():
                    sender.wallet.balance -= amount
                    sender.wallet.save()
                    recipient.wallet.balance += decimal.Decimal(r["exchanged_amount"])
                    recipient.wallet.save()
                    Transfer.objects.create(sender=sender,
                                            recipient=recipient,
                                            amount=amount,
                                            currency=sender.wallet.currency,
                                            received_currency=recipient.wallet.currency,
                                            received_amount=r["exchanged_amount"])

                messages.success(request, "Transfer Successful")

            except OperationalError:
                messages.error(request, f"Transfer operation is not possible now.")
            except ValueError as e:
                messages.error(request, e)
            except ObjectDoesNotExist as e:
                messages.error(request, f"User does not exist.")


    else:
        form = TransferForm()

    return render(request, "payapp/transfer.html", {
        "form": form,
    })

@login_required(redirect_field_name="")
def request(request):
    if request.method == "POST":
        form = RequestForm(request.POST)

        if form.is_valid():
            to_user = form.cleaned_data["username"]
            amount = form.cleaned_data["amount"]
            try:
                requester = User.objects.select_for_update().get(username=request.user.username)
                payer = User.objects.select_for_update().get(username=to_user)

                if requester == payer:
                    raise ValueError("You can't request money from yourself")

                r = requests.get(request.build_absolute_uri(reverse("convert-api", args=[requester.wallet.currency.currency_code, payer.wallet.currency.currency_code, amount])))

                if r.status_code == 400:
                    raise ValueError("Something went wrong")

                r = r.json()

                Request.objects.create(requester=requester,
                                        payer=payer,
                                        amount=amount,
                                        currency=requester.wallet.currency,
                                        received_currency=payer.wallet.currency,
                                        received_amount=r["exchanged_amount"])

                messages.success(request, "Request Successful")

            except OperationalError:
                messages.error(request, f"Transfer operation is not possible now.")
            except ValueError as e:
                messages.error(request, e)
            except ObjectDoesNotExist as e:
                messages.error(request, f"User does not exist.")

    else:
        form = RequestForm()

    return render(request, "payapp/request.html", {
        "form": form,
    })

@login_required(redirect_field_name="")
def view_request(request, id):

    try:
        myRequest = Request.objects.get(id=id)
    except ObjectDoesNotExist:
        return redirect(reverse("pending_requests_page"))

    if myRequest.status != "Pending":
        return redirect(reverse("pending_requests_page"))

    if request.user != myRequest.payer:
        return redirect(reverse("pending_requests_page"))

    if request.method == "POST":

        if request.POST.get("action") == "accept":
            try:
                requester = User.objects.select_for_update().get(username=myRequest.requester)
                payer = User.objects.select_for_update().get(username=myRequest.payer)

                if payer.wallet.balance < myRequest.received_amount:
                    raise ValueError("Not enough funds.")

                with transaction.atomic():
                    requester.wallet.balance += myRequest.amount
                    requester.wallet.save()
                    payer.wallet.balance -= myRequest.received_amount
                    payer.wallet.save()
                    myRequest.status = "Paid"
                    myRequest.save()
                    Transfer.objects.create(sender=payer,
                                            recipient=requester,
                                            amount=myRequest.received_amount,
                                            currency=myRequest.received_currency,
                                            received_currency=myRequest.currency,
                                            received_amount=myRequest.amount)

                    messages.success(request, "Request paid successfully")

            except OperationalError:
                messages.error(request, f"Transfer operation is not possible now.")
            except ValueError as e:
                messages.error(request, e)

        elif request.POST.get("action") == "decline":
            myRequest.status = "Declined"
            myRequest.save()
            messages.success(request, "Request declined successfully")

    return render(request, "payapp/viewrequest.html", {
        "request": myRequest
    })
