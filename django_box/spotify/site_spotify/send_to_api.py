from site_spotify.testClass import RpcPublisher
import site_spotify.credentials as cred


def send_to_api(message, queue):
    rpc_publish = RpcPublisher(cred.user, cred.pw, cred.ip_address)
    print(" [x] Publishing message...")
    print(message)

    response = rpc_publish.call(message, queue)
    print(" [.] Got %r" % response)

    return response.decode('utf-8')