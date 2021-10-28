from site_spotify.testClass import RunPublisher
from site_spotify.testClass import RunSubscriber
import site_spotify.credentials as cred

exchange = 'db_exchange'
push_queue = 'db1'
pull_queue = 'db2'

def process_login(request):
    if request.method == "POST":
        account = request.POST["account"]
        passw = request.POST["pw"]
        connection = RunPublisher(cred.user, cred.pw, cred.ip_address)
        
        message = f"SELECT account_name, pw FROM site_login WHERE account_name = '{account}';"
        connection.db_publish(exchange, push_queue, message)
        
        # grabbing response from rabbit
        connection = RunSubscriber(cred.user, cred.pw, cred.ip_address)
        result = connection.db_subscribe(exchange, pull_queue)

        #result = result.decode("utf-8")
        
        return result
        

        #return HttpResponseRedirect(reverse("webtest:success"))
