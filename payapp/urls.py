from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="landing_page"),
    path("history", views.history, name="transaction_history_page"),
    path("pending", views.pending, name="pending_requests_page"),
    path("transfer", views.transfer, name="transfer_page"),
    path("request", views.request, name="request_page"),
    path("view/<id>", views.view_request, name="view_request_page"),
]