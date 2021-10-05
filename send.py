#!/usr/bin/env/ python
import pika

user = '';
password = '';

credentials = pika.PlainCredentials(user, password)
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, 'testHost', credentials))
channel = connection.channel()

channel.queue_declare(queue='testQueue', durable=True)

channel.basic_publish(exchange='testExchange', routing_key='', body='Hello World!')
print(" [x] Sent 'Hello World!'")
connection.close()
