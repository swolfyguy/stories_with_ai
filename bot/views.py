from django.shortcuts import render
from django.http.request import HttpRequest
from django.contrib.auth.decorators import login_required


@login_required
def home(request: HttpRequest):
    room = request.user.username
    return render(request, template_name="home.html", context={"room_name": room})
