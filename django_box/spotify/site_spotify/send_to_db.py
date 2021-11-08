from site_spotify.PikaClasses import RpcPublisher
import site_spotify.credentials as cred

'''
The database driver which establishes an MQ rpc publish connection 
'''

def send_to_db(message, queue, delete=False):
    rpc_publish = RpcPublisher(cred.user, cred.pw, cred.ip_address)
    print(" [x] Publishing message...")
    print(message)

    if delete:
        message = "delete:"+message

    response = rpc_publish.call(message, queue)
    print(" [.] Got %r" % response)

    return response.decode('utf-8')