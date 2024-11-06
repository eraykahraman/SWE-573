# accounts/urls.py
from django.urls import path
from .views import CustomLoginView, CustomLogoutView, register_view, home_view

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("register/", register_view, name="register"),
    path("", home_view, name="home"),  # Home view
]
