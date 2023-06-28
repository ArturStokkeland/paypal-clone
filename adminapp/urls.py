from django.urls import path
from . import views

urlpatterns = [
    path("register", views.register, name="admin-register-page"),
    path("users", views.users, name="admin-user-page"),
    path("history", views.history, name="admin-history-page"),
]