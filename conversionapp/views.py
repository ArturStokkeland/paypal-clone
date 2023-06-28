from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from decimal import Decimal, InvalidOperation
from payapp.models import Currency
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

@api_view(['GET'])
def convert(request, currency1, currency2, amount):

    try:
        from_currency = Currency.objects.get(currency_code=currency1)
        to_currency = Currency.objects.get(currency_code=currency2)
        amount = Decimal(amount)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except InvalidOperation:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    exchange_rate = from_currency.exchange_rate_to_GBP / to_currency.exchange_rate_to_GBP
    exchanged_amount = amount * exchange_rate

    response_content = {
        "currency1": from_currency.currency_code,
        "currency1_exchange_rate": from_currency.exchange_rate_to_GBP,
        "currency2": to_currency.currency_code,
        "currency2_exchange_rate": to_currency.exchange_rate_to_GBP,
        "amount_to_exchange": amount,
        "exchange_rate": exchange_rate,
        "exchanged_amount": exchanged_amount,
    }
    return Response(response_content)
