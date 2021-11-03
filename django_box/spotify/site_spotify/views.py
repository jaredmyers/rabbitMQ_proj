from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
#from site_spotify.db_auth_login import process_login
from site_spotify.register_user import process_login
from site_spotify.api_test import api_test
from site_spotify.forms import RegisterForm, LoginForm, PostThread
import uuid, json, traceback
from site_spotify.logPublisher import sendLog
from site_spotify.send_to_db import send_to_db
from site_spotify.register_user import register_user
from site_spotify.process_threads import get_thread_info, get_reply_page
from site_spotify.process_threads import Thread_main, Thread_replies


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
    if request.method == 'POST':
        ## block for handling if form is registration
        form = RegisterForm(request.POST)
        if form.is_valid():
            print("register form valid")
            username = form.cleaned_data['username']
            pw = form.cleaned_data['pw']
            pw2 = form.cleaned_data['pw2']
            if not pw == pw2:
                print("passwords don't match")
                bad_login = True
                return render(request, "site_spotify/register.html", {
                    "form": form, "bad_login": bad_login
                })
            else:
                registered = register_user(username, pw)
                if registered:
                    print("user was registered")
                    print(registered)
                    sessionId = registered
                    response = render(request, "site_spotify/home.html")
                    response.set_cookie('sessionId', sessionId)
                    return response
                else:
                    print("user was not registered, dup uname")
                    bad_login = True
                    return render(request, "site_spotify/register.html", {
                        "form": form, "bad_login": bad_login
                })
        else:
            ## block for handling if form is regular login
            form = LoginForm(request.POST)
            print(request.POST)
            if form.is_valid():
                print("loginForm form valid")
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


        list_of_threads = get_thread_info()
        print("------------------------------")
        print(list_of_threads)
        print("------------------------------")
        thread_posts = []
        for thread in list_of_threads:
            j = json.loads(thread)
            object = Thread_main(j["author"], j["threadID"], j["title"], j["content"], j["date"])
            thread_posts.append(object)

        print("rendering...")
        return render(request, "site_spotify/forum.html", {
            "form": PostThread(), "thread_posts": thread_posts
        })


   #
   # Mandatory Exception
   #
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        sendLog("From Django views: " + str(e))

        return render(request, "site_spotify/login.html", {
        "form": LoginForm(), 
    })

def thread(request, id):
    thread_and_replies = get_reply_page(str(id)).split("+")
    thread = thread_and_replies[0]
    replies = thread_and_replies[1]
    j = json.loads(thread)
    thread = Thread_main(j["author"], j["threadID"], j["title"], j["content"], j["date"])

    replies = replies.split(';')
    del replies[-1]
    reply_list = []
    for reply in replies:
        j = json.loads(reply)
        object = Thread_replies(j["author"],j["content"],j["date"])
        reply_list.append(object)
    
    reply_count = len(reply_list)
        
    return render(request, "site_spotify/thread.html", {
        "thread": thread, "reply_list": reply_list, "reply_count": reply_count})


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
def testing(request):
        return render(request, "site_spotify/another_test.html", {
            "form": LoginForm(), 
    })