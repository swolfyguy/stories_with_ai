from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, LogoutView


def register(request: HttpRequest):

    form = UserCreationForm(request.POST or None)

    if request.POST:
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("home")

    context = {"form": form, "title": "Register"}
    return render(request, template_name="register.html", context=context)


class UserLoginView(LoginView):
    template_name = "login.html"
