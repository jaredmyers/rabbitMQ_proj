from django.urls import path
from . import views

app_name = 'site_spotify'
urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("apiconnect", views.apiconnect, name="apiconnect"),
    path("urlredirect", views.urlredirect, name="urlredirect")
]