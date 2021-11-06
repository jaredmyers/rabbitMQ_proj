import PikaClasses
import credentials as cred

def send_to_db(message, queue):
    rpc_publish = PikaClasses.RpcPublisher(cred.user, cred.pw, cred.ip_address)
    print(" [x] Publishing message...")
    print(message)

    response = rpc_publish.call(message, queue)
    print(" [.] Got %r" % response)

    return response.decode('utf-8')