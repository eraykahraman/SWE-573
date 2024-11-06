from django.shortcuts import render

# Create your views here.
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django import forms



class CustomLoginView(LoginView):
    template_name = "accounts/login.html"




class CustomLogoutView(LogoutView):
    template_name = "accounts/logout.html"


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django import forms

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)
            return redirect("home")  # Redirect to a home page or dashboard
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})