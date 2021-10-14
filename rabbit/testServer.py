"""
Test: Listening for messages on specific queues

"""
from testClass import RunServer

user = 'taco'
pw = 'tastegood'
ip = 'localhost'
queue = 'db2'

listener = RunServer(user, pw, ip)

listener.listen_for_messages(queue)