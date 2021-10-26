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
    #if request.session['token']:
    #    saved_tracks = api_test(request.session['token'])
    #else:
    #    print("It didn't work.")

    return render(request, "site_spotify/dashboard.html", {
        "saved_tracks": saved_tracks 
    })

def apiconnect(request):

    return render(request, "site_spotify/apiconnect.html")

def urlredirect(request):


    code = request.GET['code']
    #request.session['access_token'] = token
    
    #return HttpResponseRedirect(reverse("site_spotify:dashboard"))

    return render(request, "site_spotify/fetchtoken.html", {
        "code": code
    })