from testClass import RunSubscriber
import credentials as cred

exchange = 'exchangeAll'
log_path = '/home/it490/Desktop/project/django_box/error.log'

connection = RunSubscriber(cred.user, cred.pw, cred.ip_address)
connection.listen_fanout(exchange, log_path)