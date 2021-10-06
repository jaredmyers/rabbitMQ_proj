"""
Test: Sending a fanout message
on exchangeAll

"""

from testClass import SendFanout

user = 'taco'
pw = 'tastegood'
ip_address = 'localhost'
exchange = 'exchangeAll'

connection = SendFanout(user, pw, ip_address)

message = 'test fanout message'
 
connection.send_fanout(exchange, message)



