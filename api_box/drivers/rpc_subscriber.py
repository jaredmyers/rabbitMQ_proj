import PikaClasses
import credentials as cred

'''
The API driver which establishes an MQ rpc subscriber connection
listens for incoming API requests
'''

queue = 'api_info'
sub_conn = PikaClasses.RunSubscriber(cred.user, cred.pw, cred.ip_address)
sub_conn.rpc_subscribe(queue)