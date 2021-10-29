from testClass import ListenFanout
import credentials as cred

exchange = 'exchangeAll'
log_path = '/home/it490/Desktop/project/django/error.log'

connection = ListenFanout(cred.user, cred.pw, cred.ip_address)
connection.listen_fanout(exchange, log_path)
