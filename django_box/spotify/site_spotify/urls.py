from django.urls import path
from . import views

app_name = 'site_spotify'
urlpatterns = [
    path("", views.index, name="index"),
    path("c_home", views.c_home, name="c_home"),
    path("apiconnect", views.apiconnect, name="apiconnect"),
    path("urlredirect", views.urlredirect, name="urlredirect"),
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
    path("home", views.home, name="home"),
    path("chat", views.chat, name="chat"),
    path("forum", views.forum, name="forum"),
    path("friends", views.friends, name="friends"),
    path("stats", views.stats, name="stats"),
    path("connect", views.connect, name="connect"),
    path("logout", views.logout, name="logout"),
    path("testing", views.testing, name="testing"),
    path("thread/<int:id>", views.thread, name="thread"),
    path("room/<str:chat_recipient>", views.chatroom, name="chatroom"),
    path("sendchat", views.sendchat, name="sendchat"),
    path("getMessages/<str:room_id>", views.getMessages, name="getMessages")
]