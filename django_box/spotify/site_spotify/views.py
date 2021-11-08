from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
#from site_spotify.db_auth_login import process_login
from site_spotify.register_user import register_user, process_login
from site_spotify.api_test import api_test
from site_spotify.forms import RegisterForm, LoginForm, PostThread, PostReply, AddFriend, SendChat, ProcessChatData
import uuid, json, traceback
from site_spotify.logPublisher import sendLog
from site_spotify.send_to_db import send_to_db
from site_spotify.process_threads import get_thread_info, get_reply_page, send_new_thread, send_new_reply
from site_spotify.process_threads import add_friend, get_friends, create_chat, get_username, new_chat_message, get_chat_messages
from site_spotify.process_threads import Thread_main, Thread_replies
from site_spotify.process_api import fetch_token, store_token_api, get_saved_tracks, get_stats_page
import datetime, random, json

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
        #check for valid sessionID
        if 'sessionId' in request.COOKIES:
            print('cookie detected...')
            response = send_to_db(request.COOKIES['sessionId'], 'check_session')
            print(f"response: {response}")
            if not response:
                print('cookie is false or expired')
                session_expired = True
                response = render(request, "site_spotify/login.html", {
                    "form":LoginForm(), "session_expired": session_expired })
                response.delete_cookie('sessionId')
                print("session terminated")
                return response
        else:
            print("no cookie detected")
            please_log_in = True
            return render(request, "site_spotify/login.html", {
                "form": LoginForm(), "please_log_in": please_log_in})

        
        # take in spotifys code and get api token, then store db
        if request.method == 'GET':
            if 'code' in request.GET:
                code = request.GET['code']
                token = fetch_token(code)
                response = store_token_api(token, request.COOKIES['sessionId'])
        
        
        saved_tracks = get_saved_tracks(request.COOKIES['sessionId'])
        
        print("rendering...")
        return render(request, "site_spotify/home.html", {"saved_tracks": saved_tracks})

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
            if not response:
                print('cookie is false or expired')
                session_expired = True
                response = render(request, "site_spotify/login.html", {
                    "form":LoginForm(), "session_expired": session_expired })
                response.delete_cookie('sessionId')
                print("session terminated")
                return response
        else:
            print("no cookie detected")
            return render(request, "site_spotify/login.html", {
                "form": LoginForm(), 
    })
        if request.method == 'POST':
            form = AddFriend(request.POST)
            print(request.POST)
            if form.is_valid():
                print("addfriend form valid")
                friendname = form.cleaned_data['addfriend']
                print(friendname)
                add_friend_response = add_friend(request.COOKIES['sessionId'], friendname)

        
        friends_list = get_friends(request.COOKIES['sessionId'])
        friend_number = len(friends_list)
            
        print("rendering...")
        return render(request, "site_spotify/chat.html", {
            "form": AddFriend(), "friends_list": friends_list, "friend_number": friend_number
        })

   #
   # Mandatory Exception
   #
    except Exception as e:
        print(e)
        sendLog("From Django views: " + str(e))

        return render(request, "site_spotify/login.html", {
        "form": LoginForm(), 
    })

def chatroom(request, chat_recipient):

    try:

        if 'sessionId' in request.COOKIES:
            print('cookie detected...')
            response = send_to_db(request.COOKIES['sessionId'], 'check_session')
            print(f"response: {response}")
            if not response:
                print('cookie is false or expired')
                session_expired = True
                response = render(request, "site_spotify/login.html", {
                    "form":LoginForm(), "session_expired": session_expired })
                response.delete_cookie('sessionId')
                print("session terminated")
                return response
        else:
            print("no cookie detected")
            return render(request, "site_spotify/login.html", {
                "form": LoginForm(), 
            })

        if request.method == 'POST':
            form = ProcessChatData(request.POST)
            print(request.POST)
            if form.is_valid():
                print("Process ChatData form valid")
                username = form.cleaned_data['username']
                room_id = form.cleaned_data['room_id']
                message = form.cleaned_data['message']
                new_message = new_chat_message(username, message, room_id)
            else:
                form = SendChat(request.POST)
                if form.is_valid():
                    print("send chat form valid")

                        
        
        # create chat table between two users if non-existant
        room_id = create_chat(request.COOKIES['sessionId'], chat_recipient)
        username = get_username(request.COOKIES['sessionId'])

        
        friends_list = get_friends(request.COOKIES['sessionId'])
        friend_number = len(friends_list)

        
            
        print("rendering...")
        return render(request, "site_spotify/chatroom.html", {
            "form": AddFriend(), "friends_list": friends_list, 
            "friend_number": friend_number, "chat_recipient": chat_recipient, 
            "form2": SendChat(), "room_id": room_id, "username": username
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

def getMessages(request, room_id):
    
    message_dict = get_chat_messages(room_id)

    return JsonResponse({"messages":message_dict})

def sendchat(request):
    room_id = request.POST['room_id']
    message = request.POST['message']
    username = request.POST['username']

    print("From Djangos sendchat")

    print(room_id, message, username)

    #new_message = new_chat_message(username, message, room_id)
    new_message = ''

    if new_message:
        return HttpResponse("Message send successfully!")
    else:
        return HttpResponse("Message didn't send.")


def forum(request):
    try:

        if 'sessionId' in request.COOKIES:
            print('cookie detected...')
            response = send_to_db(request.COOKIES['sessionId'], 'check_session')
            print(f"response: {response}")
            if not response:
                print('cookie is false or expired')
                session_expired = True
                response = render(request, "site_spotify/login.html", {
                    "form":LoginForm(), "session_expired": session_expired })
                response.delete_cookie('sessionId')
                print("session terminated")
                return response
        else:
            print("no cookie detected")
            return render(request, "site_spotify/login.html", {
                "form": LoginForm(), 
    })
    
        # take in and send new thread
        if request.method == "POST":
            form = PostThread(request.POST)
            if form.is_valid():
                threadname = form.cleaned_data['threadname']
                threadcontent = form.cleaned_data['threadcontent']
                send_new_thread(request.COOKIES['sessionId'], threadname, threadcontent)

        list_of_threads = get_thread_info()

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
    
    # take in and send new reply
    if request.method == "POST":
        form = PostReply(request.POST)
        if form.is_valid():
            replycontent = form.cleaned_data['replycontent']
            send_new_reply(request.COOKIES['sessionId'], str(id), replycontent)
    
    # get the thread and its replies
    thread_and_replies = get_reply_page(str(id)).split("+")
    thread = thread_and_replies[0]
    replies = thread_and_replies[1]

    #load thread from json to object
    j = json.loads(thread)
    thread = Thread_main(j["author"], j["threadID"], j["title"], j["content"], j["date"])

    # segment each reply
    replies = replies.split(';')
    del replies[-1]

    # load replies from json to reply object, create list of reply objects
    reply_list = []
    for reply in replies:
        j = json.loads(reply)
        object = Thread_replies(j["author"],j["content"],j["date"])
        reply_list.append(object)
    
    reply_count = len(reply_list)
        
    return render(request, "site_spotify/thread.html", {
        "thread": thread, "reply_list": reply_list, "reply_count": reply_count, "form": PostReply()})


def friends(request):
    try:

        if 'sessionId' in request.COOKIES:
            print('cookie detected...')
            response = send_to_db(request.COOKIES['sessionId'], 'check_session')
            print(f"response: {response}")
            if not response:
                print('cookie is false or expired')
                session_expired = True
                response = render(request, "site_spotify/login.html", {
                    "form":LoginForm(), "session_expired": session_expired })
                response.delete_cookie('sessionId')
                print("session terminated")
                return response
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
            if not response:
                print('cookie is false or expired')
                session_expired = True
                response = render(request, "site_spotify/login.html", {
                    "form":LoginForm(), "session_expired": session_expired })
                response.delete_cookie('sessionId')
                print("session terminated")
                return response
        else:
            print("no cookie detected")
            return render(request, "site_spotify/login.html", {
                "form": LoginForm(), 
    })

        get_stats_page(request.COOKIES['sessionId'])

        print("rendering...")
        return render(request, "site_spotify/stats.html")

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

def connect(request):
    try:

        if 'sessionId' in request.COOKIES:
            print('cookie detected...')
            response = send_to_db(request.COOKIES['sessionId'], 'check_session')
            print(f"response: {response}")
            if not response:
                print('cookie is false or expired')
                session_expired = True
                response = render(request, "site_spotify/login.html", {
                    "form":LoginForm(), "session_expired": session_expired })
                response.delete_cookie('sessionId')
                print("session terminated")
                return response
        else:
            print("no cookie detected")
            return render(request, "site_spotify/login.html", {
                "form": LoginForm(), 
    })

        print("rendering...")
        return render(request, "site_spotify/apiconnect.html")

   
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