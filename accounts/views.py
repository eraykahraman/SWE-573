# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy

# Existing views
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('house')  # Changed from 'home' to 'house'


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")  # Redirect to login page after logout    


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "accounts/register.html", {"form": form})

# New home view
def home_view(request):
    return render(request, "accounts/home.html")
