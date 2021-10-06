"""
Test: Listening for a fanout message
on exchangeAll

"""

from testClass import ListenFanout

user = 'taco'
pw = 'tastegood'
ip_address = 'localhost'
exchange = 'exchangeAll'

connection = ListenFanout(user, pw, ip_address)
connection.listen_fanout(exchange)