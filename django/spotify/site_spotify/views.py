from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from site_spotify.db_auth_login import process_login
from site_spotify.api_test import api_test

saved_tracks = []

# Create your views here.
def index(request):
    if request.method == "POST":
        answer = process_login(request)
        print(answer)
        if answer != 'Not Found' and answer != 'error':
            return HttpResponseRedirect(reverse("site_spotify:dashboard"))
        else:
            answer = False
    else:
        answer = None
            
    return render(request, "site_spotify/index.html", {
        "login": answer
    })

def dashboard(request):
    saved_tracks = api_test()

    return render(request, "site_spotify/dashboard.html", {
        "saved_tracks": saved_tracks 
    })
