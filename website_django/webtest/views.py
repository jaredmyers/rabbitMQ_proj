from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from webtest.testClass import RunPublisher
from webtest.testClass import RunSubscriber
import webtest.credentials as cred

datas = []
login_success = False

# Create your views here.
def index(request):
    if request.method == "POST":
        account = request.POST["account"]
        passw = request.POST["pw"]
        connection = RunPublisher(cred.user, cred.pw, cred.ip_address)
        
        message = f"SELECT account_name, pw FROM site_login WHERE account_name = '{account}';"
        connection.db_publish('db_exchange', 'db1', message)
        
        # grabbing response from rabbit
        connection = RunSubscriber(cred.user, cred.pw, cred.ip_address)
        result = connection.db_subscribe('db_exchange','db2')
        
        print(result)
        

        #return HttpResponseRedirect(reverse("webtest:success"))

    
    return render(request, "webtest/index.html")


def success(request):
    
    return render(request, "webtest/success.html", {
        "login": login_success, "datas": datas
    })
