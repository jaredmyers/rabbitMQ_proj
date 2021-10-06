"""
Test: Sending messages to specific queues

"""
from testClass import RunClient

user = 'taco'
pw = 'tastegood'
ip = 'localhost'

q = 'nothing queue1 queue2 queue3'
e = 'nothing exchange1 exchange2 exchange3'
q = q.split()
e = e.split()

choice = None

while choice != 'exit':
    connection = RunClient(user, pw, ip)

    choice = input("Enter a Queue: ")

    if choice == 'exit':
        break
    choice = int(choice)

    queue = q[choice]
    exchange = e[choice]

    message = f'test message on {queue}'

    connection.send_message(exchange, queue, message)


