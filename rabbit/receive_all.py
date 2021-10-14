"""
Test: Listening for a fanout message
on exchangeAll

"""

from testClass import ListenFanout
import credentials as cred

exchange = 'exchangeAll'

connection = ListenFanout(cred.user, cred.pw, cred.ip_address)
connection.listen_fanout(exchange)