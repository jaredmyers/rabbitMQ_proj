"""
Test: Sending a fanout message
on exchangeAll

"""

from testClass import SendFanout
import credentials as cred

exchange = 'exchangeAll'

connection = SendFanout(cred.user, cred.pw, cred.ip_address)

message = 'test fanout message'
 
connection.send_fanout(exchange, message)



