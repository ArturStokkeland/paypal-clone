from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

# Create your models here.

class Currency(models.Model):
    currency_name = models.CharField(max_length=30)
    currency_code = models.CharField(max_length=5, primary_key=True)
    currency_symbol = models.CharField(max_length=5)
    exchange_rate_to_GBP = models.DecimalField(max_digits=10, decimal_places=3)

    def __str__(self):
        return self.currency_code

    class Meta:
        verbose_name_plural = "Currencies"

class Wallet(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=1000.00) #1 trillion with 2 decimal places
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Transfer(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transfers")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received")
    amount = models.DecimalField(max_digits=13, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="currency_sent")
    received_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="currency_received")
    received_amount = models.DecimalField(max_digits=15, decimal_places=2)
    date_issued = models.DateTimeField(auto_now_add=True)

class Request(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests")
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    amount = models.DecimalField(max_digits=13, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="request_currency_sent")
    status = models.CharField(max_length=20, default="Pending")
    received_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="request_currency_received", null=True)
    received_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    date_issued = models.DateTimeField(auto_now_add=True)
