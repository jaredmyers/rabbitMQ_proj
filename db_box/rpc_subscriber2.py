from testClass import RunSubscriber
import credentials as cred

queue = 'threads'
sub_conn = RunSubscriber(cred.user, cred.pw, cred.ip_address)
sub_conn.rpc_subscribe(queue)