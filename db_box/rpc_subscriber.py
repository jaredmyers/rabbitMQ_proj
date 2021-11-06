import PikaClasses
import credentials as cred

queue = 'check_session'
sub_conn = PikaClasses.RunSubscriber(cred.user, cred.pw, cred.ip_address)
sub_conn.rpc_subscribe(queue)