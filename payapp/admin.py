from django.contrib import admin
from .models import Wallet, Currency, Transfer, Request

# Register your models here.

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("currency_code", "currency_symbol", "exchange_rate_to_GBP")

class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "currency")

admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(Transfer)
admin.site.register(Request)
