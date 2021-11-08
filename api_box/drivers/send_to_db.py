import PikaClasses
import credentials as cred
'''
The database driver which establishes an MQ rpc publisher connection
publishes triggers to be consumed by database, returns database data
'''


def send_to_db(message, queue):
    rpc_publish = PikaClasses.RpcPublisher(cred.user, cred.pw, cred.ip_address)
    print(" [x] Publishing message...")
    print(message)

    response = rpc_publish.call(message, queue)
    print(" [.] Got %r" % response)

    return response.decode('utf-8')