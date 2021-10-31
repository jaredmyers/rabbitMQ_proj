from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from site_spotify.db_auth_login import process_login
from site_spotify.api_test import api_test
from site_spotify.forms import RegisterForm, LoginForm
import uuid
from site_spotify.logPublisher import sendLog
from site_spotify.send_to_db import send_to_db

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

def c_home(request):

    bad_login = False
    if request.method =='POST':
        form = LoginForm(request.POST)
        print(request.POST)
        if form.is_valid():
            print("form valid")
            username = form.cleaned_data['username']
            pw = form.cleaned_data['pw']
            print(username, pw)

            authentication = process_login(username, pw)
            
            print(authentication)
            if not authentication:
                print("LOGIN FAIL1")
                bad_login = True
                return render(request, "site_spotify/login.html", {
                    "form": form, "bad_login": bad_login
                })
            #return HttpResponseRedirect(reverse("site_spotify:login"))
        else:
            print("form not valid")
            print("LOGIN FAIL2")
            bad_login = True
            return render(request, "site_spotify/login.html", {
                "form": form, "bad_login": bad_login
            })

    print("LOGIN SUCCESSFUL")

    sessionId = authentication

    response = render(request, "site_spotify/home.html")
    response.set_cookie('sessionId', sessionId)
    return response

    #if 'saved_tracks' not in request.session:
    #    request.session["saved_tracks"] = []

    #if request.method == 'POST':
    #    if 'token' in request.POST:
    #        token = request.POST['token']
    #        print("Django, the token is: " + token)
    #        print("sending to api...")
    #        request.session["saved_tracks"] = api_test(token)

    #if request.session['token']:
    #    saved_tracks = api_test(request.session['token'])
    #else:
    #    print("It didn't work.")

    #print("after api call....")
    #print(request.session["saved_tracks"])
    
    #return render(request, "site_spotify/dashboard.html", {
    #    "saved_tracks": request.session['saved_tracks'] 
    #})

def apiconnect(request):

    return render(request, "site_spotify/apiconnect.html")

def urlredirect(request):


    if request.method == 'GET':
        if 'code' in request.GET:
            code = request.GET['code']

    #request.session['access_token'] = token
    
    #return HttpResponseRedirect(reverse("site_spotify:dashboard"))

    return render(request, "site_spotify/fetchtoken.html", {
        "code": code
    })

def login(request):
    
    return render(request, "site_spotify/login.html", {
        "form": RegisterForm(), 
    })

def register(request):

    return render(request, "site_spotify/register.html", {
        "form": RegisterForm()

    })


# Main 5 website pages #
def home(request):
    try:

        if 'sessionId' in request.COOKIES:
            print('cookie detected...')
            response = send_to_db(request.COOKIES['sessionId'], 'check_session')
            print(f"response: {response}")
            if response == False:
                print('cookie is false')
                return render(request, "site_spotify/login.html", {"form": LoginForm()})
        else:
            print("no cookie detected")
            return render(request, "site_spotify/login.html", {
                "form": LoginForm(), 
    })

        print("rendering...")
        return render(request, "site_spotify/home.html")

   #
   # Mandatory Exception
   #
    except Exception as e:
        print(e)
        sendLog("From Django views: " + str(e))

        return render(request, "site_spotify/login.html", {
        "form": LoginForm(), 
    })
    

def chat(request):
    try:

        if 'sessionId' in request.COOKIES:
            print('cookie detected...')
            response = send_to_db(request.COOKIES['sessionId'], 'check_session')
            print(f"response: {response}")
            if response == False:
                print('cookie is false')
                return render(request, "site_spotify/login.html", {"form": LoginForm()})
        else:
            print("no cookie detected")
            return render(request, "site_spotify/login.html", {
                "form": LoginForm(), 
    })

        print("rendering...")
        return render(request, "site_spotify/chat.html")

   #
   # Mandatory Exception
   #
    except Exception as e:
        print(e)
        sendLog("From Django views: " + str(e))

        return render(request, "site_spotify/login.html", {
        "form": LoginForm(), 
    })


def forum(request):
    try:

        if 'sessionId' in request.COOKIES:
            print('cookie detected...')
            response = send_to_db(request.COOKIES['sessionId'], 'check_session')
            print(f"response: {response}")
            if response == False:
                print('cookie is false')
                return render(request, "site_spotify/login.html", {"form": LoginForm()})
        else:
            print("no cookie detected")
            return render(request, "site_spotify/login.html", {
                "form": LoginForm(), 
    })

        print("rendering...")
        return render(request, "site_spotify/forum.html")

   #
   # Mandatory Exception
   #
    except Exception as e:
        print(e)
        sendLog("From Django views: " + str(e))

        return render(request, "site_spotify/login.html", {
        "form": LoginForm(), 
    })

def friends(request):
    try:

        if 'sessionId' in request.COOKIES:
            print('cookie detected...')
            response = send_to_db(request.COOKIES['sessionId'], 'check_session')
            print(f"response: {response}")
            if response == False:
                print('cookie is false')
                return render(request, "site_spotify/login.html", {"form": LoginForm()})
        else:
            print("no cookie detected")
            return render(request, "site_spotify/login.html", {
                "form": LoginForm(), 
    })

        print("rendering...")
        return render(request, "site_spotify/friends.html")

   #
   # Mandatory Exception
   #
    except Exception as e:
        print(e)
        sendLog("From Django views: " + str(e))

        return render(request, "site_spotify/login.html", {
        "form": LoginForm(), 
    })

def stats(request):
    try:

        if 'sessionId' in request.COOKIES:
            print('cookie detected...')
            response = send_to_db(request.COOKIES['sessionId'], 'check_session')
            print(f"response: {response}")
            if response == False:
                print('cookie is false')
                return render(request, "site_spotify/login.html", {"form": LoginForm()})
        else:
            print("no cookie detected")
            return render(request, "site_spotify/login.html", {
                "form": LoginForm(), 
    })

        print("rendering...")
        return render(request, "site_spotify/stats.html")

   #
   # Mandatory Exception
   #
    except Exception as e:
        print(e)
        sendLog("From Django views: " + str(e))

        return render(request, "site_spotify/login.html", {
        "form": LoginForm(), 
    })

def connect(request):
    try:

        if 'sessionId' in request.COOKIES:
            print('cookie detected...')
            response = send_to_db(request.COOKIES['sessionId'], 'check_session')
            print(f"response: {response}")
            if response == False:
                print('cookie is false')
                return render(request, "site_spotify/login.html", {"form": LoginForm()})
        else:
            print("no cookie detected")
            return render(request, "site_spotify/login.html", {
                "form": LoginForm(), 
    })

        print("rendering...")
        return render(request, "site_spotify/stats.html")

   
   #
   # Mandatory Exception
   #
    except Exception as e:
        print(e)
        sendLog("From Django views: " + str(e))

        return render(request, "site_spotify/login.html", {
        "form": LoginForm(), 
    })

def logout(request):
    try:

        if 'sessionId' in request.COOKIES:
            print('cookie detected...')
            delete = True
            response = send_to_db(request.COOKIES['sessionId'], 'check_session', delete)
            print(f"response: {response}")
            
            response = render(request, "site_spotify/login.html", {"form":LoginForm()})
            response.delete_cookie('sessionId')
            print("rendering...")
            return response

   #
   # Mandatory Exception
   #
    except Exception as e:
        print(e)
        sendLog("From Django views: " + str(e))

        return render(request, "site_spotify/login.html", {
        "form": LoginForm(), 
    })