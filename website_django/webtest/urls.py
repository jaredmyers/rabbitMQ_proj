from django.urls import path
from . import views

app_name = "webtest"
urlpatterns = [
    path("", views.index, name="index"),
    path("success", views.success, name="success")
]