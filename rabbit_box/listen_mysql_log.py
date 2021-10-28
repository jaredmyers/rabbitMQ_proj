from testClass import ListenFanout
import credentials as cred

exchange = 'exchangeAll'
web_log_path = '/home/it490/Desktop/project/mysqltest.log'

connection = ListenFanout(cred.user, cred.pw, cred.ip_address)
connection.listen_fanout(exchange, web_log_path)