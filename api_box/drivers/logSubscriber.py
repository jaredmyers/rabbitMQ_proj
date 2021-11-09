from PikaClasses import RunSubscriber
import credentials as cred

exchange = 'exchangeAll'
log_path = './error.log'

connection = RunSubscriber(cred.user, cred.pw, cred.ip_address)
connection.listen_fanout(exchange, log_path)